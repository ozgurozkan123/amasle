FROM python:3.11-slim

# Install system dependencies and amass
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install OWASP Amass - download pre-built binary
RUN wget https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Linux_amd64.zip -O /tmp/amass.zip \
    && unzip /tmp/amass.zip -d /tmp/amass \
    && mv /tmp/amass/amass_Linux_amd64/amass /usr/local/bin/amass \
    && chmod +x /usr/local/bin/amass \
    && rm -rf /tmp/amass /tmp/amass.zip

# Verify amass is installed
RUN amass -version || echo "Amass version check"

WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment for proper binding
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the port (Render will set PORT env var)
EXPOSE 8000

CMD ["python", "server.py"]
