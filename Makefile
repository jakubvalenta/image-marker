_python_pkg = image_marker

.PHONY: test
test:  ## Run unit tests
	tox -e py38

.PHONY: lint
lint:  ## Run linting
	tox -e lint

.PHONY: tox
tox:  ## Run unit tests and linting
	tox -r

.PHONY: reformat
reformat:  ## Reformat Python code using Black
	black -l 79 --skip-string-normalization $(_python_pkg)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
