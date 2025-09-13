FROM ghcr.io/astral-sh/uv:python3.10-alpine

WORKDIR /app

COPY pyproject.toml uv.lock /app/

# Install system dependencies locally
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN uv sync --locked --no-dev

COPY . /app

EXPOSE 8000

# Run migrations and start the server
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "pharmacy_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
