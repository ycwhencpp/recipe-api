# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory
WORKDIR /recipe-docker

# Copy the requirements file
COPY requirements.txt /recipe-docker/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /recipe-docker/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["bash", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]
