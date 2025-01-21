.PHONY: lint
lint:
	mypy --install-types --non-interactive --config-file setup.cfg .
	flake8 .

.PHONY: style
style:
	black . --check --diff
	isort . -c --diff

.PHONY: format
format:
	black .
	isort .

.PHONY: flint
flint: format lint

.PHONY: migration
migration:
	alembic revision --autogenerate

.PHONY: dev-compose
dev-compose:
	docker compose -p smart_fridge -f deployment/docker-compose.local.yml up -d --build --remove-orphans

.PHONY: dev-destroy
dev-destroy:
	docker compose -p smart_fridge -f deployment/docker-compose.local.yml down -v --remove-orphans

.PHONY: bot-run
bot-run:
	PYTHONPATH=. python3 smart_fridge/bot.py
