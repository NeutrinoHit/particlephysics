#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const chromeBin =
  process.env.CHROME_BIN ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error("Usage: node scripts/check_reveal_math.mjs <deck.html> [...]");
  process.exit(2);
}

function freePort() {
  return new Promise((resolvePort, reject) => {
    const server = createServer();
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = address.port;
      server.close(() => resolvePort(port));
    });
    server.on("error", reject);
  });
}

function requestJson(url) {
  return fetch(url).then((response) => {
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }
    return response.json();
  });
}

async function waitForTarget(port, fileUrl) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try {
      const targets = await requestJson(`http://127.0.0.1:${port}/json/list`);
      const target = targets.find((entry) => entry.url === fileUrl) || targets[0];
      if (target?.webSocketDebuggerUrl) {
        return target.webSocketDebuggerUrl;
      }
    } catch {
      // Chrome is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 150));
  }
  throw new Error("Timed out waiting for Chrome DevTools target.");
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const events = new Map();

  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolveSend, rejectSend } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) {
        rejectSend(new Error(message.error.message));
      } else {
        resolveSend(message.result);
      }
      return;
    }
    if (message.method && events.has(message.method)) {
      for (const handler of events.get(message.method)) handler(message.params);
    }
  });

  return new Promise((resolveConnect, rejectConnect) => {
    ws.addEventListener("open", () => {
      resolveConnect({
        send(method, params = {}) {
          const messageId = ++id;
          ws.send(JSON.stringify({ id: messageId, method, params }));
          return new Promise((resolveSend, rejectSend) => {
            pending.set(messageId, { resolveSend, rejectSend });
          });
        },
        on(method, handler) {
          if (!events.has(method)) events.set(method, []);
          events.get(method).push(handler);
        },
        close() {
          ws.close();
        },
      });
    });
    ws.addEventListener("error", rejectConnect);
  });
}

async function checkFile(file) {
  const absolute = resolve(file);
  const fileUrl = pathToFileURL(absolute).href;
  const port = await freePort();
  const userDataDir = mkdtempSync(`${tmpdir()}/ippb-chrome-`);
  const chrome = spawn(chromeBin, [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--allow-file-access-from-files",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    fileUrl,
  ]);

  try {
    const wsUrl = await waitForTarget(port, fileUrl);
    const client = await connect(wsUrl);
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await new Promise((resolveWait) => setTimeout(resolveWait, 6000));

    const expression = `(() => new Promise(async (resolve) => {
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      for (let i = 0; i < 40; i++) {
        const renderedNow = document.querySelectorAll("mjx-container, .MathJax").length;
        if (window.MathJax && renderedNow > 0) break;
        await wait(250);
      }
      const horizontal = Array.from(document.querySelectorAll(".reveal .slides > section"));
      const leafSlides = [];
      horizontal.forEach((section, h) => {
        const vertical = Array.from(section.querySelectorAll(":scope > section"));
        if (vertical.length > 0) {
          vertical.forEach((child, v) => leafSlides.push({ h, v, section: child }));
        } else {
          leafSlides.push({ h, v: 0, section });
        }
      });
      const rendered = Array.from(document.querySelectorAll("mjx-container, .MathJax"));
      const errors = Array.from(document.querySelectorAll("mjx-merror, .merror"))
        .map((node) => node.textContent.trim())
        .filter(Boolean);
      const invisible = [];
      let slidesWithMath = 0;
      let checkedMath = 0;
      for (const item of leafSlides) {
        const mathOnSlide = Array.from(item.section.querySelectorAll(".math"));
        if (mathOnSlide.length === 0) continue;
        slidesWithMath += 1;
        if (window.Reveal) {
          window.Reveal.slide(item.h, item.v);
          await wait(120);
        }
        const renderedOnSlide = Array.from(item.section.querySelectorAll("mjx-container, .MathJax"));
        checkedMath += renderedOnSlide.length;
        renderedOnSlide.forEach((node) => {
          const rect = node.getBoundingClientRect();
          const style = getComputedStyle(node);
          if (rect.width === 0 || rect.height === 0 ||
              style.visibility === "hidden" || style.display === "none") {
            invisible.push({ h: item.h, v: item.v, text: node.textContent.trim().slice(0, 80) });
          }
        });
      }
      resolve({
        title: document.title,
        slides: leafSlides.length,
        slidesWithMath,
        mathSources: document.querySelectorAll(".math").length,
        renderedMath: rendered.length,
        checkedMath,
        errors,
        invisible: invisible.length,
        invisibleDetails: invisible.slice(0, 5)
      });
    }))()`;

    const result = await client.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    client.close();
    chrome.kill("SIGTERM");
    return result.result.value;
  } catch (error) {
    chrome.kill("SIGTERM");
    throw error;
  }
}

let failed = false;
for (const file of files) {
  const result = await checkFile(file);
  console.log(`${file}: ${JSON.stringify(result)}`);
  if (
    result.slides === 0 ||
    result.mathSources === 0 ||
    result.renderedMath === 0 ||
    result.checkedMath !== result.renderedMath ||
    result.invisible > 0 ||
    result.errors.length > 0
  ) {
    failed = true;
  }
}

process.exit(failed ? 1 : 0);
