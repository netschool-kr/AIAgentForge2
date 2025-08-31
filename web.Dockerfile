# --- Builder Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies, including Node.js and npm
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Export the frontend build
RUN reflex export --frontend-only --no-zip

# --- Final Stage ---
FROM nginx:1.25-alpine

COPY --from=builder /app/.web/build/client /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
