FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ./app ./app

# Expose the port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:socket_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
