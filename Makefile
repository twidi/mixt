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
	@pip install -e .[dev,doc]
	@mixt-post-install
	@$(MAKE) full-clean

.PHONY: dev-upgrade
dev-upgrade:  ## Upgrade all default+dev dependencies defined in setup.cfg
	@pip install --upgrade `python -c 'import setuptools; o = setuptools.config.read_configuration("setup.cfg")["options"]; print(" ".join(o["install_requires"] + o["extras_require"]["dev"]))'`
	@pip install -e .

.PHONY: lint
lint:  ## Run all linters (check-isort, check-black, mypy, flake8, pylint)
lint: check-isort check-black flake8 pylint mypy

.PHONY: mypy
mypy:  ## Run the mypy tool
	@echo "$(BOLD)Running mypy$(RESET)"
	@mypy src/

.PHONY: check-isort
check-isort:  ## Run the isort tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking isort(RESET)"
	@isort --check-only `find src/ -name '*.py' | grep -v '/codec/' | xargs grep -L '# coding: mixt'` 2>&1

.PHONY: check-black
check-black:  ## Run the black tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking black$(RESET)"
	@black --check `find src/ -name '*.py' | grep -v '/codec/' | xargs grep -L '# coding: mixt'` 2>&1

.PHONY: flake8
flake8:  ## Run the flake8 tool
	@echo "$(BOLD)Running flake8$(RESET)"
	@flake8 --format=abspath src/

.PHONY: pylint
pylint:  ## Run the pylint tool
	@echo "$(BOLD)Running pylint$(RESET)"
	@pylint src

.PHONY: pretty
pretty:  ## Run all code beautifiers (isort, black)
pretty: isort black

.PHONY: isort
isort:  ## Run the isort tool and update files that need to
	@echo "$(BOLD)Running isort$(RESET)"
	@isort `find src/ -name '*.py' | grep -v '/codec/' | xargs grep -L '# coding: mixt'`

.PHONY: black
black:  ## Run the black tool and update files that need to
	@echo "$(BOLD)Running black$(RESET)"
	@black `find src/ -name '*.py' | grep -v '/codec/' | xargs grep -L '# coding: mixt'`

.PHONY: tests test
test: tests
tests:  ## Run test tests
	@echo "$(BOLD)Running tests$(RESET)"
	@pytest tests

.PHONY: check-doc
check-doc:  ## Check if documentation is up to date
	@echo "$(BOLD)Checking documentation$(RESET)"
	@MIXT_DISABLE_DEV_MODE=1 python -m api_doc.app > docs/index.html.new
	@diff -q docs/index.html.new docs/index.html > /dev/null && (echo 'Doc is up to date'; rm docs/index.html.new) || (echo 'Doc is not up to date' 1>&2; rm docs/index.html.new; exit 1)

.PHONY: check checks
check: checks
checks:  ## Run all checkers (lint, tests, check-doc)
checks: lint tests check-doc

.PHONY: doc
doc:  ## Build the documentation and save it to docs/
	@echo "$(BOLD)Building documentation$(RESET)"
	@python -m api_doc.app > docs/index.html

.PHONY: dist
dist:  ## Build the package
	@echo "$(BOLD)Building package$(RESET)"
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

