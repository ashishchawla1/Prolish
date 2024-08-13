# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome
RUN apt-get update && apt-get install -y \
  wget \
  unzip \
  libglib2.0-0 \
  libnss3 \
  libgconf-2-4 \
  libfontconfig1 \
  && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/108.0.5359.22/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && mv chromedriver /usr/bin/chromedriver \
  && chown root:root /usr/bin/chromedriver \
  && chmod +x /usr/bin/chromedriver

# Set work directory
WORKDIR /usr/src/app

# Make port 80 available to the world outside this container
EXPOSE 80

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run the application
CMD ["python", "main.py"]