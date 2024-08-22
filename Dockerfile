FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy


# RUN apt-get update && apt-get install -y \
#     libnss3 \
#     libatk1.0-0 \
#     libatk-bridge2.0-0 \
#     libcups2 \
#     libdrm2 \
#     libxkbcommon0 \
#     libxcomposite1 \
#     libxrandr2 \
#     libgbm1 \
#     libasound2 \
#     libpangocairo-1.0-0 \
#     libgtk-3-0 \
#     libxshmfence1 \
#     libglu1-mesa \
#     libegl1 \
#     libfreetype6 \
#     libfontconfig1 \
#     libxrender1 \
#     libx11-6 \
#     libxext6 \
#     libxdamage1 \
#     libxfixes3 \
#     wget \
#     ca-certificates \
#     --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*


# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and .env file into the container
COPY requirements.txt ./
COPY .env .env


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install playwright
RUN playwright install

# Copy the contents of the current directory (apollo) into /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Define environment variables
ENV HOST=0.0.0.0
ENV PORT=8080

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]