# Introduction to Particle Physics for Baikal School

This mini-course introduces the particle-physics language needed to read processes in neutrino and astroparticle experiments. The goal is not to derive the full Standard Model Lagrangian, but to understand what particles are, how interactions are encoded, what experiments measure, and why the Standard Model is a tightly constrained quantum-field-theory construction.

## Contents

- Lecture 1: Particles, Fields, and Interactions
- Lecture 2: The Standard Model
- Handouts with control questions
- Formula sheet
- Optional local pedagogical notebooks, not published on the course site

## Python Environment

The notebooks and `src/particle_intro/` need only `numpy`, `matplotlib` and
Jupyter (`requirements.txt`). Use the shared `neutrinohit` pyenv environment or
any pyenv environment with these packages; do not create a virtual environment
inside the repository:

```bash
pyenv activate neutrinohit
pip install -r requirements.txt
```

`environment.yml` describes the same packages for conda.

## Rendering the Mini-Course

The mini-course is part of the parent `particlephysics` Quarto website: it
uses the parent `_quarto.yml`, the shared Reveal assets in `../shared/` and the
slide settings in `slides/_metadata.yml`. Rendered pages go to
`../_site/IntroParticlePhysicsBaikal/`.

From the repository root:

```bash
make intro
```

From this folder:

```bash
make render
make slides
make handouts
```

A single deck can also be rendered directly, for example
`quarto render slides/01_particles_fields_interactions.qmd`.

## Animation Exports

`animation_exports.toml` lists the slide animations exported to MP4 by
`scripts/export_animations.py` (Playwright and ffmpeg are required). The script
renders the listed decks through the parent project and records the frames
from `../_site/IntroParticlePhysicsBaikal/slides/`:

```bash
make animations
```

The MP4 files are written to `exports/animations/`.

## Running Notebooks

```bash
make notebooks
```

The notebooks are pedagogical and use toy models. They are not precision calculations.

## Project Structure

```text
IntroParticlePhysicsBaikal/
├── index.qmd
├── README.md
├── Makefile
├── animation_exports.toml
├── requirements.txt
├── environment.yml
├── references.bib
├── slides/          decks, _metadata.yml with the Reveal settings, media/
├── handouts/
├── appendices/
├── notebooks/
├── scripts/         animation export, MathJax check
├── src/particle_intro/
└── assets/css/      mini-course slide styles
```

## Physics Scope

The lectures focus on:

- particles as field quanta and quantum states;
- quantum numbers and conservation laws;
- interactions, amplitudes, and Feynman diagrams as bookkeeping;
- cross sections, decay widths, detector response, and event rates;
- Standard Model matter content and gauge structure;
- weak charged and neutral currents;
- gauge invariance as a principle for building interactions;
- Higgs condensate, vector-boson mass generation, and fermion mass parametrization;
- weak decays as Standard Model processes.

## Toy-Model Warnings

The code examples and notebooks are intentionally simple. They do not include full detector simulation, backgrounds, realistic response matrices, nuclear effects, full three-flavor matter oscillations, or precision uncertainty propagation.

## Style Notes

The local style follows the NeutrinoHit dark Reveal.js convention: black theme, compact typography, DVN/NeutrinoHit logo, footer, 1280 x 720 slides, and restrained visual elements. The canonical shared footer, logo and theme are maintained in `neutrinohit-map` and synced into `../shared/` of the parent `particlephysics` project.
