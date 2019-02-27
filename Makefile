
help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make deploy           deploy to the server configured in hosts.dev."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: deploy
deploy:
	(cd deployment; ansible-playbook setup-server.yml -i hosts.dev --vault-password-file .vault.txt)

.PHONY: format
format:
	@echo "Running black" && black --check ncdr metrics tests || exit 1

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
	pytest
