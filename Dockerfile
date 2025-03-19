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

# Install specific version of Chromium (force downgrade to version 114)
RUN apt-get update && apt-get install -y \
    chromium=114.0.5735.* \
    --allow-downgrades \
    --no-install-recommends \
    || (apt-get install -y chromium-browser=114.0.5735.* --allow-downgrades --no-install-recommends) \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver 114 (the version that matches our Chromium)
RUN wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash
ENV DISPLAY=:99

# Set Chrome binary path explicitly
ENV CHROME_BIN=/usr/bin/chromium

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# Install specific Selenium version compatible with ChromeDriver 114
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir selenium==4.9.1

# Copy application code
COPY . .

# Make sure ChromeDriver is in PATH
ENV PATH="/usr/local/bin:${PATH}"

# Expose port 8000
EXPOSE 8000

# Start Xvfb and run the application
CMD Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset & gunicorn app:app --bind 0.0.0.0:8000