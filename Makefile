
help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make deploy-prod      deploy to production with the server configured in hosts.dev."
	@echo "    make deploy-dev       deploy a development build to the server configured in hosts.dev."
	@echo "    make fix              fix formatting and import sort order."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make metrics          run the metrics importers."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: deploy-prod
deploy-prod:
	(cd deployment; ansible-playbook setup-prod.yml -i hosts.dev --vault-password-file ~/.vault.txt)

.PHONY: deploy-dev
deploy-dev:
	(cd deployment; ansible-playbook setup-dev.yml -i hosts.dev --vault-password-file ~/.vault.txt)

.PHONY: fix
fix:
	black ncdr metrics tests
	isort

.PHONY: format
format:
	@echo "Running black" && black --check ncdr metrics tests || exit 1

.PHONY: lint
lint:
	@echo "Running flake8" && flake8 --show-source || exit 1

.PHONY: metrics
metrics:
	@python manage.py import_themes data/metrics/themes.tsv
	@python manage.py import_metrics data/metrics/metrics.tsv

.PHONY: setup
setup:
	pip install -r requirements.txt
	pip install --pre -r requirements-dev.txt

.PHONY: sort
sort:
	@echo "Running Isort" && isort --check-only --diff || exit 1

.PHONY: test
test:
	pytest
