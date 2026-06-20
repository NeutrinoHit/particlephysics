# Introduction to Particle Physics for Baikal School

This mini-course introduces the particle-physics language needed to read processes in neutrino and astroparticle experiments. The goal is not to derive the full Standard Model Lagrangian, but to understand what particles are, how interactions are encoded, what experiments measure, and why neutrinos are both Standard Model particles and evidence for physics beyond its minimal form.

## Contents

- Lecture 1: Particles, Fields, and Interactions
- Lecture 2: The Standard Model and Neutrinos
- Handouts with control questions
- Formula sheet
- Three short pedagogical notebooks

## Installation

```bash
cd /Users/dmitrijnaumov/Documents/NeutrinoHit/particlephysics/IntroParticlePhysicsBaikal

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quarto can also be installed separately if the local conda package is not available.

With conda:

```bash
conda env create -f environment.yml
conda activate intro-particle-physics-baikal
```

## Rendering the Mini-Course

Render the whole mini-course:

```bash
quarto render
```

Render slide decks separately:

```bash
quarto render slides/01_particles_fields_interactions.qmd
quarto render slides/02_standard_model_neutrinos.qmd
```

Or use:

```bash
make slides
```

## Running Notebooks

```bash
make notebooks
```

The notebooks are pedagogical and use toy models. They are not precision calculations.

## Project Structure

```text
IntroParticlePhysicsBaikal/
├── _quarto.yml
├── index.qmd
├── README.md
├── Makefile
├── requirements.txt
├── environment.yml
├── references.bib
├── slides/
├── handouts/
├── notebooks/
├── src/particle_intro/
├── assets/
└── outputs/
```

## Physics Scope

The lectures focus on:

- particles as field quanta and quantum states;
- quantum numbers and conservation laws;
- interactions, amplitudes, and Feynman diagrams as bookkeeping;
- cross sections, decay widths, detector response, and event rates;
- Standard Model matter content and gauge structure;
- weak charged and neutral currents;
- Higgs vacuum expectation value and fermion mass parametrization;
- neutrino flavor, mass states, oscillations, and why the minimal Standard Model is incomplete.

## Toy-Model Warnings

The code examples and notebooks are intentionally simple. They do not include full detector simulation, backgrounds, realistic response matrices, nuclear effects, full three-flavor matter oscillations, or precision uncertainty propagation.

## Style Notes

The local style follows the NeutrinoHit dark Reveal.js convention: black theme, compact typography, DVN/NeutrinoHit logo, footer, 1280 x 720 slides, and restrained visual elements. The canonical shared footer/logo assets are maintained in `neutrinohit-map` and synced into the parent `particlephysics` project.
