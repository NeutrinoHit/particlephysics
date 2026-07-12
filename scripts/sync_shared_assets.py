#!/usr/bin/env python3
from pathlib import Path
import shutil


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SOURCE = ROOT / "neutrinohit-map" / "assets" / "reveal"

COPIES = [
    ("neutrinohit-reveal-footer.js", PROJECT / "shared" / "reveal"),
    ("neutrinohit-timed-captions.js", PROJECT / "shared" / "reveal"),
    ("neutrinohit-reveal-quiz.css", PROJECT / "shared" / "reveal"),
    ("dvnlogo.png", PROJECT / "shared" / "reveal"),
    ("neutrinohit-reveal.scss", PROJECT / "shared" / "styles"),
    ("neutrinohit-reveal-footer.js", PROJECT / "IntroParticlePhysicsBaikal" / "assets" / "reveal"),
    ("neutrinohit-timed-captions.js", PROJECT / "IntroParticlePhysicsBaikal" / "assets" / "reveal"),
    ("dvnlogo.png", PROJECT / "IntroParticlePhysicsBaikal" / "assets" / "logos"),
]


def main() -> None:
    for name, target_dir in COPIES:
        source = SOURCE / name
        if not source.exists():
            raise FileNotFoundError(f"Missing shared asset: {source}")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / name
        shutil.copy2(source, target)
        print(f"{source} -> {target}")


if __name__ == "__main__":
    main()
