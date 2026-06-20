# Particle Physics

Independent Quarto/GitHub Pages project for NeutrinoHit particle-physics materials.

Published site:

```text
https://neutrinohit.github.io/particlephysics/
```

## Structure

- `IntroParticlePhysicsBaikal/` - two-lecture Baikal School mini-course moved from `talks/`.
- `ParticlePhysics/` - scaffold for the future 16-lecture particle-physics course with RU/EN, slides, and book directories.
- `shared/` - synced NeutrinoHit reveal assets and shared styles.
- `analytics/` - Cloudflare analytics include for published pages.

## Build

```bash
quarto render
```

or:

```bash
make render
```

To render only the Baikal mini-course:

```bash
make intro
```

## Shared Assets

The shared foundation lives in `../neutrinohit-map/assets/reveal/`. Sync it into this repository with:

```bash
make sync-shared
```

Project-specific Quarto settings remain in this repository. The shared sync only updates common reveal footer/logo/style assets.
