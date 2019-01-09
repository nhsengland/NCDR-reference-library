
help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: lint
lint:
	@echo "Running flake8" && flake8 --show-source || exit 1

.PHONY: setup
setup:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: sort
sort:
	@echo "Running Isort" && isort --check-only --diff || exit 1

.PHONY: test
test:
	python manage.py test
