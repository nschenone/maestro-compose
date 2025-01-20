.DEFAULT_GOAL := help

PYTHON_INTERPRETER = python
SHELL=/bin/bash
CONDA_ENV ?= maestro
SRC ?= maestro_compose
TESTS ?= tests
CONDA_PY_VER ?= 3.9
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

#################################################################################
# COMMANDS                                                                      #
#################################################################################

.PHONY: help
help: ## Display available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all
all:
	$(error please pick a target)

.PHONY: install-requirements
install-requirements: ## Install all requirements needed for development
	poetry install
	
release: clean fmt ## Release python package to PyPi
	$(MAKE) tag
	poetry publish --build
	
.PHONY: clean
clean: ## Delete all compiled Python files
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist

.PHONY: fmt
fmt: ## Format the code (using black and isort)
	@echo "Running black fmt..."
	black $(SRC)
	isort $(SRC)

.PHONY: lint
lint: fmt-check flake8 ## Run lint on the code

.PHONY: fmt-check
fmt-check: ## Format and check the code (using black and isort)
	@echo "Running black+isort fmt check..."
	black --check --diff $(SRC)
	isort --check --diff $(SRC)

.PHONY: flake8
flake8: ## Run flake8 lint
	@echo "Running flake8 lint..."
	flake8 $(SRC)

.PHONY: bump
bump: clean fmt ## Publish python package to PyPi with a patch version bump
	@version_type=$(or $(VERSION),patch); \
	echo "Bumping version: $$version_type"; \
	poetry version $$version_type; \

.PHONY: bump-minor
bump-minor: ## Publish python package to PyPi with a minor version bump
	$(MAKE) bump VERSION=minor

.PHONY: bump-major
bump-major: ## Publish python package to PyPi with a major version bump
	$(MAKE) bump VERSION=major

.PHONY: tag
tag: ## Create and push a new tag based on the current poetry version
	@version=$$(poetry version -s); \
	echo "Creating tag: $$version"; \
	git tag $$version; \
	git push origin $$version; \
	echo "Tag $$version created and pushed to origin"; \
