FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Poetry files and README.md
COPY pyproject.toml poetry.lock* README.md /app/

# Configure poetry to not use virtualenvs
RUN poetry config virtualenvs.create false

# Install dependencies without installing the project
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 5000

# Run the app
CMD ["flask", "run", "--host=0.0.0.0"]