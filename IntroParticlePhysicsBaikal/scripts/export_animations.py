#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlparse


def fail(message: str) -> "NoReturn":
    raise SystemExit(message)


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def load_manifest(path: Path) -> tuple[dict, list[dict]]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    export = data.get("export", {})
    animations = data.get("animation", [])
    if not animations:
        fail(f"No [[animation]] entries in {path}")

    required = {"source", "selector", "duration", "fps", "output"}
    outputs: set[str] = set()
    for index, item in enumerate(animations, start=1):
        missing = required - item.keys()
        if missing:
            fail(f"Animation #{index} is missing: {', '.join(sorted(missing))}")
        if float(item["duration"]) <= 0 or int(item["fps"]) <= 0:
            fail(f"Animation #{index} has non-positive duration/fps")
        capture = str(item.get("capture", export.get("capture", "element")))
        if capture not in {"element", "viewport"}:
            fail(f"Animation #{index} has unsupported capture mode: {capture}")
        fragment_mode = str(item.get("fragment_mode", export.get("fragment_mode", "sequence")))
        if fragment_mode not in {"sequence", "all"}:
            fail(f"Animation #{index} has unsupported fragment mode: {fragment_mode}")
        output = str(item["output"])
        if output in outputs:
            fail(f"Duplicate output in manifest: {output}")
        outputs.add(output)
    return export, animations


def rendered_html(course_root: Path, source: str) -> Path:
    # The course is rendered by the parent particlephysics website project.
    site_dir = course_root.parent / "_site" / course_root.name
    return site_dir / Path(source).with_suffix(".html")


def prepare_slide(page, selector: str, startup_ms: int) -> None:
    page.wait_for_function("typeof Reveal !== 'undefined' && Reveal.isReady()")
    page.clock.run_for(startup_ms)
    result = page.evaluate(
        """
        (selector) => {
          const target = document.querySelector(selector);
          if (!target) return {ok: false, reason: `selector not found: ${selector}`};
          const section = target.closest('section');
          if (!section) return {ok: false, reason: `no Reveal section for: ${selector}`};
          const indices = Reveal.getIndices(section);
          Reveal.slide(indices.h, indices.v, 0);
          let ancestor = target.closest('.fragment');
          while (ancestor) {
            ancestor.classList.add('visible', 'current-fragment');
            ancestor = ancestor.parentElement?.closest('.fragment') || null;
          }
          return {ok: true};
        }
        """,
        selector,
    )
    if not result["ok"]:
        fail(result["reason"])
    page.clock.run_for(100)
    page.evaluate("() => document.fonts && document.fonts.ready")



def isolate_target(page, selector: str) -> None:
    result = page.evaluate(
        """
        (selector) => {
          const target = document.querySelector(selector);
          if (!target) return {ok: false, reason: `selector not found: ${selector}`};

          for (const node of document.body.querySelectorAll('*')) {
            if (node === target || target.contains(node) || node.contains(target)) continue;
            node.style.setProperty('visibility', 'hidden', 'important');
          }
          return {ok: true};
        }
        """,
        selector,
    )
    if not result["ok"]:
        fail(result["reason"])


def set_fragment_state(
    page,
    selector: str,
    mode: str,
    time_ms: int,
    duration_ms: int,
) -> None:
    result = page.evaluate(
        """
        ({selector, mode, timeMs, durationMs}) => {
          const target = document.querySelector(selector);
          if (!target) return {ok: false, reason: `selector not found: ${selector}`};

          const fragments = [...target.querySelectorAll('.fragment')];
          const groups = [];
          const groupByKey = new Map();

          fragments.forEach((node, position) => {
            const raw = node.getAttribute('data-fragment-index');
            const numeric = raw !== null && Number.isFinite(Number(raw)) ? Number(raw) : null;
            const key = numeric === null ? `auto-${position}` : `index-${numeric}`;
            if (!groupByKey.has(key)) {
              const group = {
                key,
                order: numeric === null ? 1000000000 + position : numeric,
                position,
                nodes: [],
              };
              groupByKey.set(key, group);
              groups.push(group);
            }
            groupByKey.get(key).nodes.push(node);
          });

          groups.sort((a, b) => a.order - b.order || a.position - b.position);
          let lastVisibleGroup = -1;

          groups.forEach((group, groupIndex) => {
            const revealMs =
              mode === 'all'
                ? 0
                : Math.round(durationMs * (groupIndex + 1) / (groups.length + 1));
            const visible = timeMs >= revealMs;
            if (visible) lastVisibleGroup = groupIndex;

            for (const node of group.nodes) {
              node.dataset.animationExportRevealMs = String(revealMs);
              node.style.setProperty('transition', 'none', 'important');
              node.classList.toggle('visible', visible);
              node.classList.remove('current-fragment');
            }
          });

          if (lastVisibleGroup >= 0) {
            for (const node of groups[lastVisibleGroup].nodes) {
              node.classList.add('current-fragment');
            }
          }

          return {ok: true, fragmentGroups: groups.length};
        }
        """,
        {
            "selector": selector,
            "mode": mode,
            "timeMs": time_ms,
            "durationMs": duration_ms,
        },
    )
    if not result["ok"]:
        fail(result["reason"])


def inline_local_svg_images(page, selector: str) -> None:
    images = page.evaluate(
        """
        (selector) => {
          const target = document.querySelector(selector);
          if (!target) return [];
          const nodes = [];
          if (target.matches?.('img[src]')) nodes.push(target);
          nodes.push(...target.querySelectorAll('img[src]'));
          return nodes
            .filter((img) => new URL(img.src).pathname.toLowerCase().endsWith('.svg'))
            .map((img, index) => {
              const marker = `animation-export-svg-${index}`;
              img.dataset.animationExportSvg = marker;
              return {marker, src: img.src};
            });
        }
        """,
        selector,
    )

    for image in images:
        parsed = urlparse(image["src"])
        if parsed.scheme != "file":
            fail(f"Animated SVG must be a local file for deterministic export: {image['src']}")
        svg_path = Path(unquote(parsed.path))
        if not svg_path.is_file():
            fail(f"SVG source is missing: {svg_path}")
        svg_text = svg_path.read_text(encoding="utf-8")
        result = page.evaluate(
            """
            ({marker, svgText}) => {
              const img = document.querySelector(`[data-animation-export-svg="${marker}"]`);
              if (!img) return {ok: false, reason: `marked SVG image not found: ${marker}`};
              const rect = img.getBoundingClientRect();
              const computed = getComputedStyle(img);
              const parsed = new DOMParser().parseFromString(svgText, 'image/svg+xml');
              const source = parsed.documentElement;
              if (!source || source.nodeName.toLowerCase() !== 'svg') {
                return {ok: false, reason: `invalid SVG document: ${img.src}`};
              }

              const svg = document.importNode(source, true);
              const classes = new Set([
                ...svg.classList,
                ...img.classList,
              ]);
              if (classes.size) svg.setAttribute('class', [...classes].join(' '));

              for (const attr of img.attributes) {
                if (['src', 'class', 'alt', 'width', 'height', 'data-animation-export-svg'].includes(attr.name)) {
                  continue;
                }
                svg.setAttribute(attr.name, attr.value);
              }
              if (img.alt && !svg.hasAttribute('aria-label')) svg.setAttribute('aria-label', img.alt);

              svg.style.cssText = img.style.cssText;
              svg.style.width = `${rect.width}px`;
              svg.style.height = `${rect.height}px`;
              svg.style.display = computed.display;
              svg.style.verticalAlign = computed.verticalAlign;
              img.replaceWith(svg);
              return {ok: true};
            }
            """,
            {"marker": image["marker"], "svgText": svg_text},
        )
        if not result["ok"]:
            fail(result["reason"])


def initialize_animation_timelines(page, selector: str) -> None:
    result = page.evaluate(
        """
        (selector) => {
          const target = document.querySelector(selector);
          if (!target) return {ok: false, reason: `selector not found: ${selector}`};

          window.__animationExportStarts = new WeakMap();
          for (const animation of target.getAnimations({subtree: true})) {
            const isTransition =
              typeof CSSTransition !== 'undefined' && animation instanceof CSSTransition;
            try {
              if (isTransition) {
                animation.finish();
              } else {
                window.__animationExportStarts.set(animation, 0);
                animation.currentTime = 0;
                animation.pause();
              }
            } catch (_) {
              // An animation can disappear while Reveal updates fragment state.
            }
          }

          const svgs = [];
          if (target.matches?.('svg')) svgs.push(target);
          svgs.push(...target.querySelectorAll('svg'));
          for (const svg of svgs) {
            if (typeof svg.pauseAnimations === 'function') svg.pauseAnimations();
            if (typeof svg.setCurrentTime === 'function') svg.setCurrentTime(0);
          }
          return {ok: true};
        }
        """,
        selector,
    )
    if not result["ok"]:
        fail(result["reason"])


def seek_animation_timelines(page, selector: str, time_ms: int) -> None:
    result = page.evaluate(
        """
        ({selector, timeMs}) => {
          const target = document.querySelector(selector);
          if (!target) return {ok: false, reason: `selector not found: ${selector}`};

          if (!window.__animationExportStarts) window.__animationExportStarts = new WeakMap();
          for (const animation of target.getAnimations({subtree: true})) {
            const isTransition =
              typeof CSSTransition !== 'undefined' && animation instanceof CSSTransition;
            if (isTransition) {
              try { animation.finish(); } catch (_) {}
              continue;
            }
            try {
              if (!window.__animationExportStarts.has(animation)) {
                const effectTarget = animation.effect?.target;
                const fragment = effectTarget?.closest?.('.fragment');
                const revealMs =
                  fragment && target.contains(fragment)
                    ? Number(fragment.dataset.animationExportRevealMs || timeMs)
                    : timeMs;
                window.__animationExportStarts.set(animation, revealMs);
              }
              const startMs = window.__animationExportStarts.get(animation) || 0;
              animation.currentTime = Math.max(0, timeMs - startMs);
              animation.pause();
            } catch (_) {
              // Ignore animations that are no longer active at this exact frame.
            }
          }

          const svgs = [];
          if (target.matches?.('svg')) svgs.push(target);
          svgs.push(...target.querySelectorAll('svg'));
          for (const svg of svgs) {
            if (typeof svg.pauseAnimations === 'function') svg.pauseAnimations();
            if (typeof svg.setCurrentTime === 'function') svg.setCurrentTime(timeMs / 1000);
          }
          return {ok: true};
        }
        """,
        {"selector": selector, "timeMs": time_ms},
    )
    if not result["ok"]:
        fail(result["reason"])

def encode_mp4(
    frame_dir: Path,
    fps: int,
    output: Path,
    course_root: Path,
    output_width: int,
    output_height: int,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frame_dir / "frame-%06d.png"),
            "-vf",
            (
                f"scale={output_width}:{output_height}:"
                "force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={output_width}:{output_height}:"
                "(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ],
        course_root,
    )


def export_one(browser, course_root: Path, defaults: dict, item: dict) -> None:
    source = str(item["source"])
    selector = str(item["selector"])
    duration = float(item["duration"])
    fps = int(item["fps"])
    output = course_root / str(item["output"])
    capture = str(item.get("capture", defaults.get("capture", "element")))
    fragment_mode = str(item.get("fragment_mode", defaults.get("fragment_mode", "sequence")))
    html = rendered_html(course_root, source)
    if not html.exists():
        fail(f"Rendered HTML is missing: {html}")

    page = browser.new_page(
        viewport={
            "width": int(defaults.get("viewport_width", 1280)),
            "height": int(defaults.get("viewport_height", 720)),
        },
        reduced_motion="no-preference",
        device_scale_factor=float(defaults.get("device_scale_factor", 2.5)),
    )
    page.clock.install()
    page.goto(html.resolve().as_uri(), wait_until="load")
    prepare_slide(page, selector, int(defaults.get("startup_ms", 1000)))
    inline_local_svg_images(page, selector)
    isolate_target(page, selector)
    duration_ms = round(duration * 1000)
    set_fragment_state(page, selector, fragment_mode, 0, duration_ms)
    initialize_animation_timelines(page, selector)

    locator = page.locator(selector).first
    locator.wait_for(state="visible")
    frame_count = max(1, math.ceil(duration * fps))
    previous_ms = 0

    with tempfile.TemporaryDirectory(prefix="neutrinohit-animation-") as temp:
        frame_dir = Path(temp)
        for frame in range(frame_count):
            target_ms = round(frame * 1000 / fps)
            delta_ms = target_ms - previous_ms
            if delta_ms:
                page.clock.run_for(delta_ms)
            previous_ms = target_ms
            set_fragment_state(page, selector, fragment_mode, target_ms, duration_ms)
            seek_animation_timelines(page, selector, target_ms)
            frame_path = str(frame_dir / f"frame-{frame:06d}.png")
            if capture == "viewport":
                page.screenshot(path=frame_path, full_page=False, scale="device")
            else:
                locator.screenshot(path=frame_path, scale="device")
        encode_mp4(
            frame_dir,
            fps,
            output,
            course_root,
            int(defaults.get("output_width", 1280)),
            int(defaults.get("output_height", 720)),
        )

    page.close()
    print(f"exported {output.relative_to(course_root)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export committed Reveal/HTML animations to MP4."
    )
    parser.add_argument(
        "--manifest",
        default="animation_exports.toml",
        help="Manifest path relative to the course root",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Export only outputs whose path contains this substring; repeatable",
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Use existing ../_site/IntroParticlePhysicsBaikal/slides/*.html instead of running Quarto",
    )
    args = parser.parse_args()

    if sys.version_info < (3, 11):
        fail("Python 3.11+ is required (tomllib).")
    if shutil.which("quarto") is None and not args.no_render:
        fail("quarto is required unless --no-render is used")
    if shutil.which("ffmpeg") is None:
        fail("ffmpeg is required")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fail(
            "playwright is required: "
            "python -m pip install playwright && "
            "python -m playwright install chromium"
        )

    course_root = Path(__file__).resolve().parent.parent
    defaults, animations = load_manifest(course_root / args.manifest)
    if args.only:
        animations = [
            item
            for item in animations
            if any(token in str(item["output"]) for token in args.only)
        ]
        if not animations:
            fail("--only did not match any manifest outputs")

    sources = sorted({str(item["source"]) for item in animations})
    if not args.no_render:
        for source in sources:
            run(["quarto", "render", source], course_root)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for item in animations:
                export_one(browser, course_root, defaults, item)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
