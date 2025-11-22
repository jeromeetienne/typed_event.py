help: ## Show this help message
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

###############################################################################

test: lint ## Run pytest on the tests/ directory
	pytest tests/ -W ignore::DeprecationWarning

test_verbose: lint ## Run pytest in verbose mode on the tests/ directory
	pytest tests/ -W ignore::DeprecationWarning -v 

###############################################################################

lint: ## Run pyright on the source, examples, and tests directories
	pyright ./src ./examples ./tests