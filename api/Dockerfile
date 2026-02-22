FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /api

# Install system dependencies (build-essential needed for some scikit-learn/pandas components)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Use a virtualenv to keep the build clean
RUN python -m venv /opt/venv

# Install heavy requirements first to leverage caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:3001", "--timeout", "120", "app:app"]