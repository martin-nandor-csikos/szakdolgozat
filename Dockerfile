# Use an official Python image as the base
FROM python:3.11-slim

# Install system dependencies for Chrome and other tools
RUN apt-get update && \
    apt-get install -y wget gnupg2 curl unzip && \
    # Install Chrome
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    # Install ChromeDriver
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) && \
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    # Clean up
    apt-get remove -y wget unzip curl gnupg2 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_BIN=/usr/local/bin/chromedriver

# Set the working directory
WORKDIR /app

# Copy the project files
COPY ./src /app/src

# Copy dependencies
COPY dependencies.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/dependencies.txt

# Set the entrypoint
ENTRYPOINT ["python", "-u", "src/main.py"]