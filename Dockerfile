FROM python:3.9-slim

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    chromium \
    chromium-driver

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Command to run when container starts
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]