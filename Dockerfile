FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set display port for Xvfb
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a modified version of app.py that includes timeout handling
RUN cp app.py app.py.original && \
    sed -i 's/subprocess.run\(\["python", "paste.py", betting_code], check=True\)/subprocess.run\(["python", "paste.py", betting_code], check=True, timeout=60\)/' app.py && \
    echo 'import signal' >> paste.py.tmp && \
    echo 'signal.alarm(120)  # Set a timeout of 120 seconds' >> paste.py.tmp && \
    cat paste.py >> paste.py.tmp && \
    mv paste.py.tmp paste.py && \
    chmod +x paste.py

# Create an entrypoint script that starts Xvfb before running the app
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &' >> /app/entrypoint.sh && \
    echo 'exec gunicorn app:app --bind 0.0.0.0:8000 --timeout 120 --workers 2' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set environment variables to improve performance
ENV PYTHONUNBUFFERED=1
ENV WEB_CONCURRENCY=2
ENV GUNICORN_CMD_ARGS="--workers=2 --timeout=120"
ENV CHROME_IGNORE_VERSION_MISMATCH=true

# Expose port 8000
EXPOSE 8000

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]