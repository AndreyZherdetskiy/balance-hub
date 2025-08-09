FROM python:3.12-slim

ENV POETRY_VERSION=1.7.1

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}
WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
