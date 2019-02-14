
help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: format
format:
	@echo "Running black" && black --check ncdr csv_schema metrics || exit 1

.PHONY: lint
lint:
	@echo "Running flake8" && flake8 --show-source || exit 1

.PHONY: setup
setup:
	pip install -r requirements.txt
	pip install --pre -r requirements-dev.txt

.PHONY: sort
sort:
	@echo "Running Isort" && isort --check-only --diff || exit 1

.PHONY: test
test:
	python manage.py test
