# Particle Physics

Independent Quarto project for NeutrinoHit particle-physics materials.

Published site:

```text
https://neutrinohit.github.io/particlephysics/
```

## Structure

- `IntroParticlePhysicsBaikal/` - two-lecture Baikal School mini-course moved from `talks/`.
- `ParticlePhysics/` - scaffold for the future 16-lecture particle-physics course with RU/EN, slides, and book directories. Each `slides/` folder keeps its Reveal settings in `_metadata.yml`; each `book/` folder is a Quarto book project with the shared NeutrinoHit book design.
- `shared/` - synced NeutrinoHit Reveal assets, Reveal theme, and the book LaTeX preamble.
- `analytics/` - Cloudflare analytics include for published pages.

## Build

```bash
make site
```

The complete site, including the HTML books, is written to `_site/`.
`make books` renders only the RU/EN books.

A push to `main` publishes the site automatically. `workflow_dispatch`
allows the publication to be run manually again.

To render only the Baikal mini-course:

```bash
make intro
```

## Shared Assets

The shared foundation lives in `../neutrinohit-map/assets/reveal/` and
`../neutrinohit-map/assets/books/`. The local copies in `shared/` and
`ParticlePhysics/*/book/assets/` are refreshed by the canonical
`neutrinohit-map` sync scripts:

```bash
make check-shared
make sync-shared
```

Project-specific Quarto settings remain in this repository.
