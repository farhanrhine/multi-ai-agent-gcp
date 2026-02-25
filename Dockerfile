## Parent image
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

## Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

## Copy project files
COPY . .

## Install dependencies using uv
RUN uv sync --frozen

## Used PORTS
EXPOSE 8501
EXPOSE 9999

## Run the app
CMD ["uv", "run", "main.py"]