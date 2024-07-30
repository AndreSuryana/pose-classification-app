# Stage 1: Build Stage
FROM python:3.10-slim AS build

WORKDIR /app

# Install dependencies with cache
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --timeout=120 -r requirements.txt

# Copy the application files
COPY . .
RUN ls -R /app

# Stage 2: Final Stage
FROM python:3.10-slim

WORKDIR /app

# Copy only the necassary files from the build stage
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app /app

# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port that the app runs on
EXPOSE ${API_PORT}

# Run the application with Gunicorn
CMD [ "sh", "-c", "gunicorn -w 1 -k sync -b ${API_HOST}:${API_PORT} app:app" ]

# Run the application
# CMD [ "python", "app.py" ]