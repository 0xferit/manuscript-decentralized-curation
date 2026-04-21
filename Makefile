PYTHON ?= python3
QUARTO ?= quarto

ANALYSIS_STAMP := analysis/out/.analysis-complete
ANALYSIS_INPUTS := analysis/run_all.py requirements.txt paper.qmd projects/rpgf/design.md projects/truth-post/blueprint.md
ANALYSIS_REQUIRED := analysis/out/eval_summary.md analysis/out/reading_time.md analysis/out/reading_time_blueprint.md analysis/out/reading_time_rpgf.md analysis/out/metadata.json
ANALYSIS_FIG_REQUIRED := analysis/fig/e1_adversarial.png analysis/fig/e1_challenger_ev.png analysis/fig/e1_detection_sensitivity.png analysis/fig/e1_false_survival.png analysis/fig/e2_adversarial.png analysis/fig/e2_competence_filter.png analysis/fig/e2_prime_adversarial.png analysis/fig/e2_prime_competence_filter.png analysis/fig/e2_prime_relevance_error.png analysis/fig/e2_prime_sigma_sweep.png analysis/fig/e2_prime_trojan.png analysis/fig/e2_relevance_error.png analysis/fig/e3_nonfalsifiable.png analysis/fig/e4a_author_reputation.png analysis/fig/e4b_reputation_attack.png analysis/fig/e4d_cross_domain_scoping.png
ANALYSIS_ALL_REQUIRED := $(ANALYSIS_REQUIRED) $(ANALYSIS_FIG_REQUIRED)

.PHONY: setup analysis metadata reading-time summary render-html render-pdf render check-invariants verify-fast verify-full clean

setup:
	$(PYTHON) -m pip install -r requirements.txt

analysis:
	@mkdir -p analysis/out
	@current_hash="$$( $(PYTHON) -c "import hashlib, pathlib; h=hashlib.sha256(); [h.update(pathlib.Path(path).read_bytes()) for path in '$(ANALYSIS_INPUTS)'.split()]; print(h.hexdigest())" )"; \
	needs_run=0; \
	if [ ! -f "$(ANALYSIS_STAMP)" ]; then needs_run=1; fi; \
	for output in $(ANALYSIS_ALL_REQUIRED); do \
		if [ ! -f "$$output" ]; then needs_run=1; fi; \
	done; \
	if [ "$$needs_run" -eq 0 ]; then \
		cached_hash="$$(cat "$(ANALYSIS_STAMP)")"; \
		if [ "$$current_hash" != "$$cached_hash" ]; then needs_run=1; fi; \
	fi; \
	if [ "$$needs_run" -eq 1 ]; then \
		echo "Regenerating analysis outputs"; \
		$(PYTHON) analysis/run_all.py full && \
		printf '%s\n' "$$current_hash" > "$(ANALYSIS_STAMP)"; \
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
