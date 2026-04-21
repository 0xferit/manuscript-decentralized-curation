PYTHON ?= python3
QUARTO ?= quarto

ANALYSIS_STAMP := analysis/out/.analysis-complete
ANALYSIS_INPUTS := analysis/run_all.py requirements.txt paper.qmd projects/rpgf/design.md projects/truth-post/blueprint.md
ANALYSIS_REQUIRED := analysis/out/eval_summary.md analysis/out/reading_time.md analysis/out/reading_time_blueprint.md analysis/out/reading_time_rpgf.md analysis/out/metadata.json

.PHONY: setup analysis metadata reading-time summary render-html render-pdf render check-invariants verify-fast verify-full clean

setup:
	$(PYTHON) -m pip install -r requirements.txt

analysis:
	@mkdir -p analysis/out
	@needs_run=0; \
	if [ ! -f "$(ANALYSIS_STAMP)" ]; then needs_run=1; fi; \
	for output in $(ANALYSIS_REQUIRED); do \
		if [ ! -f "$$output" ]; then needs_run=1; fi; \
	done; \
	if [ "$$needs_run" -eq 0 ]; then \
		for input in $(ANALYSIS_INPUTS); do \
			if [ "$$input" -nt "$(ANALYSIS_STAMP)" ]; then needs_run=1; break; fi; \
		done; \
	fi; \
	if [ "$$needs_run" -eq 1 ]; then \
		echo "Regenerating analysis outputs"; \
		$(PYTHON) analysis/run_all.py full && \
		touch "$(ANALYSIS_STAMP)"; \
	else \
		echo "Analysis outputs are up to date"; \
	fi

metadata:
	$(PYTHON) analysis/run_all.py metadata

reading-time:
	$(PYTHON) analysis/run_all.py reading-time

summary:
	$(PYTHON) analysis/run_all.py summary

render-html: analysis
	$(QUARTO) render --to html

render-pdf: analysis
	$(QUARTO) render --to pdf

render: analysis
	$(QUARTO) render

check-invariants:
	$(PYTHON) scripts/check_repo_invariants.py

verify-fast: check-invariants reading-time
	@test -f analysis/out/reading_time.md
	@test -f analysis/out/reading_time_blueprint.md
	@test -f analysis/out/reading_time_rpgf.md

verify-full: check-invariants render-html

clean:
	rm -rf outputs analysis/out analysis/fig
