FROM python:3.12-slim

WORKDIR /app

# Install build essentials and libpq for PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY . .

RUN pip install --no-cache-dir -e .

EXPOSE 8000 8101 8102

CMD ["python", "scripts/start_all.py"]
