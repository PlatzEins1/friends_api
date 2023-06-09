# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the command to start the Django tests
CMD ["python", "manage.py", "test", "friendService"]

# Run the command to start the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

