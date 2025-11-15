# Crisis Network Analysis - Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/networks data/results \
    logs results/networks results/visualizations

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Create a non-root user
RUN useradd -m -u 1000 analyst && \
    chown -R analyst:analyst /app

USER analyst

# Default command
CMD ["python", "-c", "print('Crisis Network Analysis Container Ready!')"]

# For Jupyter notebook access, use:
# CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
