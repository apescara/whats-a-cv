FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN useradd --create-home --uid 10001 app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

USER app
EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "whats_a_cv.app:app", "--host", "0.0.0.0", "--port", "8000"]
