.PHONY: render slides handouts notebooks math-check clean

render:
	quarto render

slides:
	quarto render slides/01_particles_fields_interactions.qmd
	quarto render slides/02_standard_model.qmd

handouts:
	quarto render handouts/01_questions_particles_interactions.qmd
	quarto render handouts/02_questions_standard_model.qmd
	quarto render handouts/formula_sheet.qmd

notebooks:
	jupyter nbconvert --execute notebooks/01_event_rates_and_cross_sections.ipynb --to notebook --inplace
	jupyter nbconvert --execute notebooks/02_decay_law_and_lifetime.ipynb --to notebook --inplace
	jupyter nbconvert --execute notebooks/03_neutrino_oscillation_probability.ipynb --to notebook --inplace

math-check:
	node scripts/check_reveal_math.mjs outputs/slides/01_particles_fields_interactions.html outputs/slides/02_standard_model.html

clean:
	rm -rf outputs/*
	find . -name ".quarto" -type d -prune -exec rm -rf {} +
