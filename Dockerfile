FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install gcc -y

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# These environment variables should be provided at runtime via:
# - docker run --env-file .env
# - docker-compose environment/env_file
# - Kubernetes secrets/configmaps
# - Cloud Run environment variables

ENV GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

EXPOSE 8000

ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["fastapi", "run", "src/presentation/api/main.py"]
