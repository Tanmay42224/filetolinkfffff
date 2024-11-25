# Base Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Debugging step to verify files
RUN ls -al /app

# Command to run the application
CMD ["python", "utils_bot.py"]
