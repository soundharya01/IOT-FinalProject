# Dockerfile

# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and requirements file into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirments_db.txt

# Run the Python script when the container starts
CMD ["python", "Consumer_code.py"]

