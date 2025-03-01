FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src

# Install vim (or nano) to allow text editing in the container
RUN apt-get update && apt-get install -y vim

# Copy the requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ./ ./

# Expose the port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:server_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]