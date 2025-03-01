Build the image

docker build -t fastapi-socketio-app .

run the container

docker run -p 8000:8000 fastapi-socketio-app



##
Volume update for hot reload
docker run -p 8000:8000 -v $(pwd):/app fastapi-socketio-app


Runing using
docker-compose up



TODO add a debugger configuration.
