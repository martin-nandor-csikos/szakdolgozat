# Use an official Python image as the base
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    libnss3 libxi6 libgbm1 libasound2 \
    libxrandr2 libxss1 libxtst6 \
    fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ENV CHROMEDRIVER_VERSION=120.0.6099.71

### install chrome
RUN apt-get update && apt-get install -y wget && apt-get install -y zip
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

### install chromedriver
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip \
  && unzip chromedriver-linux64.zip && rm -dfr chromedriver_linux64.zip \
  && mv /chromedriver-linux64/chromedriver /usr/bin/chromedriver \
  && chmod +x /usr/bin/chromedriver

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Set the working directory
WORKDIR /app

# Copy the project files
COPY ./src /app/src

# Copy dependencies
COPY dependencies.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/dependencies.txt
