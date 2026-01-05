# Development stage
FROM python:3.13-slim AS development

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

# Production stage
FROM python:3.13-slim AS production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Databricks CLI
RUN curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Copy only production files
COPY bundles/ ./bundles/
COPY databricks.yml .

# Set environment variables
ENV PATH="/root/.databricks/bin:${PATH}"

# Default command
CMD ["databricks", "bundle", "validate"]
