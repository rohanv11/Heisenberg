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

# Set default environment variables for production (safer defaults)
ENV DEBUG_MODE=False
ENV HOT_RELOAD=False

# Start the application - using shell script to conditionally enable hot reload
CMD sh -c "if [ \"$HOT_RELOAD\" = \"true\" ]; then \
  uvicorn app.main:server_app --host 0.0.0.0 --port 8000 --reload; \
else \
  uvicorn app.main:server_app --host 0.0.0.0 --port 8000; \
fi"
