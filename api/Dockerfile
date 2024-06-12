# Dockerfile for Flask API
FROM python:3.10

WORKDIR /app

# Installing python libraries using cache to reduce build time
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

EXPOSE ${API_PORT}

CMD [ "python", "app.py" ]