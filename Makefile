.PHONY: dev stop test clean

dev:
	docker compose up --build

stop:
	docker compose down

test:
	cd agent && PYTHONPATH=src uv run pytest
	cd web && npm run lint

clean:
	docker compose down --volumes --remove-orphans
	rm -rf -- .whats-a-cv
