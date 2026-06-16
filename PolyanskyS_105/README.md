# QR Code Generator

## Description
Microservice web application for QR code generation.

## Architecture
- **Nginx** - entry point (port 8080)
- **Frontend** - user interface (HTML)
- **Backend** - API for request processing (Flask)
- **Worker** - QR code generation service (long task)

## Run
```bash
docker-compose up --build
