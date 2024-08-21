FROM mcr.microsoft.com/playwright:v1.30.0

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and .env file into the container
COPY requirements.txt ./
COPY .env .env

# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the current directory (apollo) into /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Define environment variables
ENV HOST=0.0.0.0
ENV PORT=8080

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]