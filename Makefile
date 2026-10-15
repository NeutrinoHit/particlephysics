.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= python3
NEUTRINOHIT_MAP ?= ../neutrinohit-map
BOOKS := ParticlePhysics/ru/book ParticlePhysics/en/book

.PHONY: help sync-shared check-shared site render books intro particle-course math-check clean

help: ## Show available targets
	@printf '%s\n' 'Available targets:'
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync-shared: ## Refresh shared Reveal and book assets from ../neutrinohit-map
	$(PYTHON) $(NEUTRINOHIT_MAP)/scripts/sync_reveal_assets.py --target particlephysics
	$(PYTHON) $(NEUTRINOHIT_MAP)/scripts/sync_book_assets.py --target particlephysics

check-shared: ## Compare shared assets with ../neutrinohit-map without writing
	$(PYTHON) $(NEUTRINOHIT_MAP)/scripts/sync_reveal_assets.py --check --target particlephysics
	$(PYTHON) $(NEUTRINOHIT_MAP)/scripts/sync_book_assets.py --check --target particlephysics

site: ## Render the whole Particle Physics site and the HTML books into _site
	rm -rf _site
	$(QUARTO) render
	$(MAKE) books
	test -s _site/index.html
	test -s _site/IntroParticlePhysicsBaikal/index.html
	test -s _site/ParticlePhysics/index.html
	test -s _site/ParticlePhysics/ru/book/index.html
	test -s _site/ParticlePhysics/en/book/index.html

render: site ## Render the whole Particle Physics site

books: ## Render the RU/EN HTML books into _site/ParticlePhysics/*/book
	for book in $(BOOKS); do $(QUARTO) render $$book --to html || exit 1; done

intro: ## Render the Baikal mini-course through the site project
	$(QUARTO) render IntroParticlePhysicsBaikal/index.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/slides/02_standard_model.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/01_questions_particles_interactions.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/02_questions_standard_model.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/handouts/formula_sheet.qmd
	$(QUARTO) render IntroParticlePhysicsBaikal/appendices/massive_photon_weight.qmd

particle-course: ## Render the 16-lecture course scaffold and its books
	$(QUARTO) render ParticlePhysics/index.qmd
	$(QUARTO) render ParticlePhysics/ru/slides/index.qmd
	$(QUARTO) render ParticlePhysics/en/slides/index.qmd
	$(MAKE) books

math-check: ## Check MathJax rendering in the Baikal mini-course slide decks
	node IntroParticlePhysicsBaikal/scripts/check_reveal_math.mjs \
	  _site/IntroParticlePhysicsBaikal/slides/01_particles_fields_interactions.html \
	  _site/IntroParticlePhysicsBaikal/slides/02_standard_model.html

clean: ## Remove generated build artifacts
	rm -rf _site .quarto .make-tmp
	rm -rf IntroParticlePhysicsBaikal/outputs IntroParticlePhysicsBaikal/.quarto
	rm -rf ParticlePhysics/*/book/_book ParticlePhysics/*/book/.quarto
