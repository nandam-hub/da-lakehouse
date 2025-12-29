FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Databricks CLI
RUN curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy project files
COPY . .

# Install pre-commit hooks
RUN pre-commit install

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/root/.databricks/bin:${PATH}"

# Default command
CMD ["pytest", "tests/"]
