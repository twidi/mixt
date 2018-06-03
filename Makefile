PROJECT_NAME := $(shell python setup.py --name)
PROJECT_VERSION := $(shell python setup.py --version)

BOLD := \033[1m
RESET := \033[0m

default: help

.PHONY : help
help:  ## Show this help
	@echo "$(BOLD)Mixt Makefile$(RESET)"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -h ':\s\+##' Makefile | column -tn -s# | awk -F ":" '{ print "  $(BOLD)" $$1 "$(RESET)" $$2 }'


.PHONY: install
install:  ## Install the project in the current environment, with its dependencies
	@echo "$(BOLD)Installing $(PROJECT_NAME) $(PROJECT_VERSION)$(RESET)"
	@pip install .

.PHONY: dev
dev:  ## Install the project in the current environment, with its dependencies, including the ones needed in a development environment
	@echo "$(BOLD)Installing $(PROJECT_NAME) $(PROJECT_VERSION) in dev mode$(RESET)"
	@pip install -e .[dev]
	@mixt-post-install

.PHONY: dev-upgrade
dev-upgrade:  ## Upgrade all default+dev dependencies defined in setup.cfg
	@pip install --upgrade `python -c 'import setuptools; o = setuptools.config.read_configuration("setup.cfg")["options"]; print(" ".join(o["install_requires"] + o["extras_require"]["dev"]))'`
	@pip install -e .

.PHONY: lint
lint:  ## Run all linters (check-black, mypy, flake8, pylint)
lint: check-black flake8 pylint mypy

.PHONY: mypy
mypy:  ## Run the mypy tool
	@echo "$(BOLD)Running mypy$(RESET)"
	@mypy src/

.PHONY: check-black
check-black:  ## Run the black tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking black$(RESET)"
	@black --check `find src/ -name '*.py' | grep -v '/pyxl/' | xargs grep -L '# coding: mixt'` 2>&1

.PHONY: black
black:  ## Run the black tool and update files that need to
	@echo "$(BOLD)Running black$(RESET)"
	@black `find src/ -name '*.py' | grep -v '/pyxl/' | xargs grep -L '# coding: mixt'`

.PHONY: flake8
flake8:  ## Run the flake8 tool
	@echo "$(BOLD)Running flake8$(RESET)"
	@flake8 --format=abspath src/

.PHONY: pylint
pylint:  ## Run the pylint tool
	@echo "$(BOLD)Running pylint$(RESET)"
	@pylint src

.PHONY: tests test
test: tests
tests:  ## Run test tests
	@echo "$(BOLD)Running tests$(RESET)"
	@pytest tests

.PHONY: dist
dist:  ## Build the package
	@python setup.py sdist bdist_wheel

.PHONY: clean
clean:  ## Clean python build related directories and files
	@echo "$(BOLD)Cleaning$(RESET)"
	@rm -rf build dist $(PROJECT_NAME).egg-info

.PHONY: full-clean
full-clean:  ## Like "clean" but will clean some other generated directories or files
full-clean: clean
	@echo "$(BOLD)Full cleaning$(RESET)"
	find ./ -type d  \( -name '__pycache__' -or -name '.pytest_cache' -or -name '.mypy_cache'  \) -print0 | xargs -tr0 rm -r

