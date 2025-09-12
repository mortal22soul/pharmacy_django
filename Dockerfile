# Python base image
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files first
COPY pyproject.toml uv.lock /app/

# Sync dependencies (installs into system)
RUN uv sync --frozen --system

# Copy project
COPY . /app

EXPOSE 8000

CMD ["gunicorn", "pharmacy_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
