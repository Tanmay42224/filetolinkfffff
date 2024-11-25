# Use the official Python 3.10 slim image as the base
FROM python:3.10.8-slim-buster

# Set environment variables to avoid Python buffering (optional but helps with logs)
ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies (e.g., git) and upgrade apt packages in one layer
RUN apt update && apt upgrade -y && apt install -y git && rm -rf /var/lib/apt/lists/*

# Set the working directory to /filetolinkfffff
WORKDIR /filetolinkfffff

# Copy the requirements file to the container
COPY requirements.txt /filetolinkfffff/requirements.txt

# Install Python dependencies without cache
RUN apk update && apk add build-base
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /filetolinkfffff

# Command to run your bot
CMD ["python", "bot.py"]
