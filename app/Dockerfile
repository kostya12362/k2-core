# --- Build Stage ---
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/tmp/poetry_cache'

ENV WORKDIR=/app
ENV PYTHONPATH=$WORKDIR/src

WORKDIR $WORKDIR

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only dependency files for better caching
COPY pyproject.toml poetry.lock ./
COPY Makefile ./

# Install only production dependencies
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy the rest of the application
COPY migrations ./migrations
COPY src ./src

# Run the app via direct commands
CMD ["make", "start-api-prod"]