#!/bin/bash

# Run all tests
pytest -xvs

# Run specific test file
# pytest -xvs tests/services/test_room_service.py

# Run with coverage
# pytest -xvs --cov=app tests/