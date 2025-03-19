# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code after dependencies
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
