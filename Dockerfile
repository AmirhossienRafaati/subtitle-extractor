FROM python:3.10-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of the app files
COPY . /app/

# Expose the port that Flask is running on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
