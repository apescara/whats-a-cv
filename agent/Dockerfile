FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN useradd --create-home --uid 10001 app
RUN mkdir -p /workspace/.whats-a-cv && chown -R app:app /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY docker-entrypoint.py ./
RUN uv sync --frozen --no-dev

EXPOSE 8000
ENTRYPOINT ["python", "/app/docker-entrypoint.py"]
CMD ["uv", "run", "--no-sync", "uvicorn", "whats_a_cv.app:app", "--host", "0.0.0.0", "--port", "8000"]
