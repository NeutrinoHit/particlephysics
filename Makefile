.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= python3

.PHONY: help sync-shared site render intro particle-course math-check clean

help: ## Show available targets
	@printf '%s\n' 'Available targets:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync-shared: ## Sync shared NeutrinoHit assets from ../neutrinohit-map
	$(PYTHON) scripts/sync_shared_assets.py

site: ## Render the whole Particle Physics site into _site
	$(QUARTO) render

render: site ## Render the whole Particle Physics site

intro: sync-shared ## Render the moved Baikal mini-course through the site project
	$(QUARTO) render IntroParticlePhysicsBaikal/index.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/slides/02_standard_model.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/01_questions_particles_interactions.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/02_questions_standard_model.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/formula_sheet.qmd

particle-course: sync-shared ## Render the empty 16-lecture course scaffold
	$(QUARTO) render ParticlePhysics/index.qmd
	$(QUARTO) render ParticlePhysics/ru/book/index.qmd
	$(QUARTO) render ParticlePhysics/ru/slides/index.qmd
	$(QUARTO) render ParticlePhysics/en/book/index.qmd
	$(QUARTO) render ParticlePhysics/en/slides/index.qmd

math-check: ## Check MathJax rendering in the Baikal mini-course slide decks
	node IntroParticlePhysicsBaikal/scripts/check_reveal_math.mjs \
	  _site/IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.html \
	  _site/IntroParticlePhysicsBaikal/slides/02_standard_model.html

clean: ## Remove generated build artifacts
	rm -rf _site .quarto .make-tmp
	rm -rf IntroParticlePhysicsBaikal/outputs IntroParticlePhysicsBaikal/.quarto
	rm -rf ParticlePhysics/**/_book ParticlePhysics/**/.quarto
