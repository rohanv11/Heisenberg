# Rockefeller - A Monopoly-like Board Game

Rockefeller is a multiplayer online board game inspired by Monopoly, built with FastAPI and Centrifugo.

## Features

- Property trading and management
- In-game stock market
- Real-time multiplayer gameplay
- Custom game configurations
- Property development (houses and hotels)

## Tech Stack

- **Backend:** FastAPI (Python)
- **Real-time Communication:** Centrifugo
- **Deployment:** Docker

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.12+

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Heisenberg
   ```

2. Create a `.env` file based on the `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to set your configuration values.

3. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. The game server will be available at http://localhost:8000 and the Centrifugo admin interface at http://localhost:8001.

## Docker Commands

### Build the image
```bash
docker build -t heisenberg .
```

### Run the container
```bash
docker run -p 8000:8000 heisenberg
```

### Run with hot reload
```bash
docker run -p 8000:8000 -v $(pwd):/usr/src heisenberg
```

### Run with Docker Compose
```bash
docker-compose up
```

## API Documentation

- OpenAPI documentation is available at http://localhost:8000/docs
- ReDoc documentation is available at http://localhost:8000/redoc

## Development

### Running Locally (Without Docker)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m app.main
   ```

## Project Structure

```
Heisenberg/
├── app/                 # Application package
│   ├── api/             # API endpoints
│   ├── config/          # Configuration
│   ├── core/            # Core functionality
│   ├── game/            # Game logic
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── tests/               # Tests
├── .env.example         # Example environment variables
├── centrifugo.json      # Centrifugo configuration
├── docker-compose.yml   # Docker Compose definition
├── Dockerfile           # Docker definition
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## TODO
- Add debugger configuration



⏺ To test, start, and build the game server:

  1. Build the Docker image:
  docker build -t heisenberg .

  2. Start the server with Docker Compose:
  docker-compose up -d

  3. Test the server:
    - Run automated tests: ./run_tests.sh
    - Manual API testing: visit http://localhost:8000/docs
    - Make requests using curl or Postman to endpoints like:
        - Create room: POST http://localhost:8000/api/rooms
      - List rooms: GET http://localhost:8000/api/rooms
  4. Check logs if needed:
  docker-compose logs -f

  The server will be running at http://localhost:8000 and Centrifugo at http://localhost:8001.

  