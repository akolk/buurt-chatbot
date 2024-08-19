# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variable to specify the host
ENV DASH_HOST=0.0.0.0

LABEL org.opencontainers.image.description="Dit is een demonstrator die tegen Kadaster endpoints praat en cartgpt een beetje na aapt"

# Run app.py when the container launches
#CMD ["python", "app_buurt.py"]
CMD ["python", "index.py"]
