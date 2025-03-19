FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libnss3 \
    libxss1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium
RUN apt-get update && apt-get install -y chromium \
    && rm -rf /var/lib/apt/lists/*

# Set display port for Xvfb
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy chromedriver.exe and application code
COPY chromedriver.exe /usr/local/bin/chromedriver
COPY . .

# Make chromedriver executable
RUN chmod +x /usr/local/bin/chromedriver

# Create a wrapper script to modify the python code
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'sed -i "s/driver = webdriver.Chrome(options=chrome_options)/from selenium.webdriver.chrome.service import Service\nservice = Service(executable_path=\"\/usr\/local\/bin\/chromedriver\")\ndriver = webdriver.Chrome(service=service, options=chrome_options)/" /app/paste.py' >> /app/entrypoint.sh && \
    echo 'Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &' >> /app/entrypoint.sh && \
    echo 'gunicorn app:app --bind 0.0.0.0:8000' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set environment variable to ignore version mismatch
ENV CHROME_IGNORE_VERSION_MISMATCH=true

# Expose port 8000
EXPOSE 8000

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]