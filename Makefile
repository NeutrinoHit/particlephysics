.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= python3
QUARTO_HOME ?= $(CURDIR)/.make-tmp/quarto-home
QUARTO_ENV ?= HOME="$(QUARTO_HOME)" XDG_CACHE_HOME="$(QUARTO_HOME)/.cache"

.PHONY: help sync-shared render intro particle-course math-check clean

help: ## Show available targets
	@printf '%s\n' 'Available targets:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync-shared: ## Sync shared NeutrinoHit assets from ../neutrinohit-map
	$(PYTHON) scripts/sync_shared_assets.py

render: sync-shared ## Render the whole Particle Physics site
	$(QUARTO_ENV) $(QUARTO) render

intro: sync-shared ## Render the moved Baikal mini-course through the site project
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/index.qmd
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.qmd
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/slides/02_standard_model_neutrinos.qmd
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/handouts/01_questions_particles_interactions.qmd
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/handouts/02_questions_standard_model_neutrinos.qmd
	$(QUARTO_ENV) $(QUARTO) render IntroParticlePhysicsBaikal/handouts/formula_sheet.qmd

particle-course: sync-shared ## Render the empty 16-lecture course scaffold
	$(QUARTO_ENV) $(QUARTO) render ParticlePhysics/index.qmd
	$(QUARTO_ENV) $(QUARTO) render ParticlePhysics/ru/book/index.qmd
	$(QUARTO_ENV) $(QUARTO) render ParticlePhysics/ru/slides/index.qmd
	$(QUARTO_ENV) $(QUARTO) render ParticlePhysics/en/book/index.qmd
	$(QUARTO_ENV) $(QUARTO) render ParticlePhysics/en/slides/index.qmd

math-check: ## Check MathJax rendering in the Baikal mini-course slide decks
	node IntroParticlePhysicsBaikal/scripts/check_reveal_math.mjs \
	  _site/IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.html \
	  _site/IntroParticlePhysicsBaikal/slides/02_standard_model_neutrinos.html

clean: ## Remove generated build artifacts
	rm -rf _site .quarto .make-tmp
	rm -rf IntroParticlePhysicsBaikal/outputs IntroParticlePhysicsBaikal/.quarto
	rm -rf ParticlePhysics/**/_book ParticlePhysics/**/.quarto
