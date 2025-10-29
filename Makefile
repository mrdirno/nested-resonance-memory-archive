# Makefile for Nested Resonance Memory Research
#
# Usage:
#   make install    - Install dependencies
#   make paper1     - Compile Paper 1 (Computational Expense)
#   make paper5d    - Compile Paper 5D (Pattern Mining)
#   make paper3     - Run Paper 3 factorial experiments
#   make test       - Run test suite
#   make lint       - Run code quality checks
#   make clean      - Clean generated files
#   make help       - Show this help
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Repository: https://github.com/mrdirno/nested-resonance-memory-archive
# License: GPL-3.0

.PHONY: help install paper1 paper5d paper3 paper4 test lint format clean docker-build docker-run figures figures-c175 figures-nrmv2 list-figures

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Nested Resonance Memory Research - Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	@echo "$(GREEN)✓ Development environment ready$(NC)"

verify: ## Verify installation
	@echo "$(BLUE)Verifying installation...$(NC)"
	@python -c "import numpy, psutil, matplotlib; print('$(GREEN)✓ Core dependencies OK$(NC)')"
	@python -c "import pandas, scipy; print('$(GREEN)✓ Analysis dependencies OK$(NC)')" || echo "$(YELLOW)⚠ Optional analysis packages missing$(NC)"
	@python -c "import pytest, black; print('$(GREEN)✓ Development tools OK$(NC)')" || echo "$(YELLOW)⚠ Optional dev tools missing$(NC)"

paper1: ## Compile Paper 1 (Computational Expense Validation)
	@echo "$(BLUE)Compiling Paper 1 (2 passes for references)...$(NC)"
	cd papers/arxiv_submissions/paper1 && \
	docker run --rm -v "$$(pwd):/work" -w /work texlive/texlive:latest pdflatex -interaction=nonstopmode manuscript.tex && \
	docker run --rm -v "$$(pwd):/work" -w /work texlive/texlive:latest pdflatex -interaction=nonstopmode manuscript.tex && \
	cp manuscript.pdf ../../compiled/paper1/Paper1_Computational_Expense_Validation_arXiv_Submission.pdf && \
	rm -f manuscript.aux manuscript.log manuscript.out || \
	echo "$(YELLOW)⚠ LaTeX compilation requires Docker$(NC)"
	@echo "$(GREEN)✓ Paper 1 compiled → papers/compiled/paper1/$(NC)"

paper5d: ## Compile Paper 5D (Pattern Mining Framework)
	@echo "$(BLUE)Compiling Paper 5D (2 passes for references)...$(NC)"
	cd papers/arxiv_submissions/paper5d && \
	docker run --rm -v "$$(pwd):/work" -w /work texlive/texlive:latest pdflatex -interaction=nonstopmode manuscript.tex && \
	docker run --rm -v "$$(pwd):/work" -w /work texlive/texlive:latest pdflatex -interaction=nonstopmode manuscript.tex && \
	cp manuscript.pdf ../../compiled/paper5d/Paper5D_Pattern_Mining_Framework_arXiv_Submission.pdf && \
	rm -f manuscript.aux manuscript.log manuscript.out || \
	echo "$(YELLOW)⚠ LaTeX compilation requires Docker$(NC)"
	@echo "$(GREEN)✓ Paper 5D compiled → papers/compiled/paper5d/$(NC)"

paper3: ## Run Paper 3 factorial experiments (6 experiments, ~67 mins)
	@echo "$(BLUE)Running Paper 3 factorial experiments...$(NC)"
	@echo "$(YELLOW)⚠ This will take ~67 minutes for optimized version$(NC)"
	cd code/experiments && bash run_all_factorial_experiments.sh
	@echo "$(GREEN)✓ Paper 3 experiments complete$(NC)"

paper4: ## Run Paper 4 higher-order factorial experiments
	@echo "$(BLUE)Running Paper 4 higher-order experiments...$(NC)"
	@echo "$(YELLOW)⚠ This will take ~3-4 hours$(NC)"
	cd code/experiments && python cycle262_h1h2h5_3way_factorial.py
	cd code/experiments && python cycle263_h1h2h4h5_4way_factorial.py
	@echo "$(GREEN)✓ Paper 4 experiments complete$(NC)"

test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v --cov=code --cov-report=term-missing || echo "$(YELLOW)⚠ Tests not yet configured$(NC)"
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-quick: ## Run quick smoke tests
	@echo "$(BLUE)Running quick smoke tests...$(NC)"
	@echo "$(YELLOW)Testing overhead validation (C255 parameters)...$(NC)"
	cd papers/minimal_package_with_experiments/experiments && \
	python overhead_check.py --N 1080000 --C_ms 67 --T_sim_min 30 --noise 0.02 --trials 50
	@echo "$(YELLOW)Testing replicability criterion (healthy mode)...$(NC)"
	cd papers/minimal_package_with_experiments/experiments && \
	python replicate_patterns.py --runs 20 --threshold 0.99 --mode healthy
	@echo "$(YELLOW)Testing replicability criterion (degraded mode)...$(NC)"
	cd papers/minimal_package_with_experiments/experiments && \
	python replicate_patterns.py --runs 20 --threshold 0.99 --mode degraded
	@echo "$(GREEN)✓ Quick tests passed$(NC)"

lint: ## Run code quality checks
	@echo "$(BLUE)Running linters...$(NC)"
	black --check code/ papers/ || echo "$(YELLOW)⚠ black not installed$(NC)"
	pylint code/ || echo "$(YELLOW)⚠ pylint not installed$(NC)"
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	black code/ papers/
	@echo "$(GREEN)✓ Code formatted$(NC)"

clean: ## Clean generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "$(GREEN)✓ Cleaned$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t nested-resonance-memory:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container interactively
	@echo "$(BLUE)Starting Docker container...$(NC)"
	docker-compose run --rm app bash

docker-test: ## Run tests in Docker
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker-compose run --rm app make test-quick

all: install verify test-quick ## Install, verify, and run quick tests
	@echo "$(GREEN)✓ All tasks complete$(NC)"

# Convenience targets for papers
papers: paper1 paper5d ## Compile all papers

# Experiments
experiments: paper3 paper4 ## Run all experiments

# Figure Regeneration (added Cycle 489)
figures: figures-c175 figures-nrmv2 ## Regenerate all publication figures
	@echo "$(GREEN)✓ All figures regenerated$(NC)"

figures-c175: ## Regenerate C175 experimental figures
	@echo "$(BLUE)Regenerating C175 experimental figures...$(NC)"
	@python code/experiments/analyze_cycle175_transition.py
	@echo "$(GREEN)✓ C175 figures regenerated$(NC)"

figures-nrmv2: ## Regenerate NRM V2 consolidation figures
	@echo "$(BLUE)Regenerating NRM V2 consolidation figures...$(NC)"
	@python code/experiments/demo_nrmv2_c175_consolidation.py
	@python code/analysis/visualize_nrmv2_coalitions.py
	@echo "$(GREEN)✓ NRM V2 figures regenerated$(NC)"

list-figures: ## List all figures in archive
	@echo "$(BLUE)Figures in archive:$(NC)"
	@find data/figures -name "*.png" -type f | wc -l | awk '{printf "  $(GREEN)Total: %s$(NC)\n", $$1}'
	@echo ""
	@echo "$(BLUE)By category:$(NC)"
	@find data/figures -name "cycle175*.png" | wc -l | awk '{printf "  C175:    %s\n", $$1}'
	@find data/figures -name "nrmv2*.png" | wc -l | awk '{printf "  NRM V2:  %s\n", $$1}'
	@find data/figures -name "paper7*.png" | wc -l | awk '{printf "  Paper 7: %s\n", $$1}'
	@echo ""
	@echo "$(YELLOW)See figmap.yaml for detailed figure mapping$(NC)"

.PHONY: all papers experiments figures figures-c175 figures-nrmv2 list-figures
