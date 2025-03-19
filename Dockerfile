FROM python:3.9-slim

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Get the installed Chromium version
RUN CHROME_VERSION=$(chromium --version | awk '{print $2}') && \
    echo "Chromium version installed: $CHROME_VERSION"

# Install the correct ChromeDriver version
RUN CHROME_VERSION=$(chromium --version | awk '{print $2}') && \
    CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run when container starts
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
