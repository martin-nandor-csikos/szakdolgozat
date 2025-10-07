# Use an official Python image as the base
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    libnss3 libxi6 libgbm1 libasound2 \
    libxrandr2 libxss1 libxtst6 \
    fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project files
COPY ./src /app/src

# Copy dependencies
COPY dependencies.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/dependencies.txt

# Install Spacy models (hungarian and english)
RUN python -m spacy download en_core_web_lg
RUN pip install hu_core_news_lg@https://huggingface.co/huspacy/hu_core_news_lg/resolve/main/hu_core_news_lg-any-py3-none-any.whl