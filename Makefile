.PHONY: infra-up infra-down api-install api-dev api-test web-install web-dev web-build

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

api-install:
	cd services/api && python -m pip install -e '.[dev]'

api-dev:
	cd services/api && uvicorn app.main:app --reload

api-test:
	cd services/api && pytest

web-install:
	npm install

web-dev:
	npm run web:dev

web-build:
	npm run web:build
