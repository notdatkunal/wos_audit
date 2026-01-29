# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for pyodbc and FreeTDS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    && rm -rf /var/lib/apt/lists/*

# Configure the ODBC driver for Sybase
# We name it "Adaptive Server Enterprise" to match the default in database.py
RUN printf "[Adaptive Server Enterprise]\n\
Description = FreeTDS driver for Sybase\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
UsageCount = 1\n" > /etc/odbcinst.ini

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8089

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]
