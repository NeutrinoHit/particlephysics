# The mini-course is rendered through the parent particlephysics project
# (../_quarto.yml); pages are written to ../_site/IntroParticlePhysicsBaikal/.

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
SITE_DIR := ../_site/IntroParticlePhysicsBaikal

.PHONY: render slides handouts notebooks math-check animations clean

render:
	$(MAKE) -C .. intro

slides:
	$(QUARTO) render slides/01_particles_fields_interactions.qmd
	$(QUARTO) render slides/02_standard_model.qmd

handouts:
	$(QUARTO) render handouts/01_questions_particles_interactions.qmd
	$(QUARTO) render handouts/02_questions_standard_model.qmd
	$(QUARTO) render handouts/formula_sheet.qmd

notebooks:
	jupyter nbconvert --execute notebooks/01_event_rates_and_cross_sections.ipynb --to notebook --inplace
	jupyter nbconvert --execute notebooks/02_decay_law_and_lifetime.ipynb --to notebook --inplace
	jupyter nbconvert --execute notebooks/03_neutrino_oscillation_probability.ipynb --to notebook --inplace

math-check:
	node scripts/check_reveal_math.mjs $(SITE_DIR)/slides/01_particles_fields_interactions.html $(SITE_DIR)/slides/02_standard_model.html

animations:
	$(PYTHON) scripts/export_animations.py

clean:
	rm -rf $(SITE_DIR) outputs
	find . -name ".quarto" -type d -prune -exec rm -rf {} +
