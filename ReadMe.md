## Python Fast API + MySQL

A FastAPI-based REST API for user management with JWT authentication, email validation, and MySQL database integration.

## Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and Object-Relational Mapping (ORM)
- **Pydantic** - Data validation and settings management
- **Pydantic Settings** - Configuration management with environment variables
- **PyJWT** - JSON Web Token (JWT) encoding and decoding
- **bcrypt** - Password hashing and verification
- **email-validator** - Email validation library
- **python-dotenv** - Load environment variables from .env files
- **uvicorn** - ASGI web server
- **MySQL** - Database (via SQLAlchemy)

## Installation

```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings pyjwt bcrypt email-validator python-dotenv
```

## Running the Application

```powershell
python -m uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

- `POST /api/v1/user` - Create a new user
- `POST /api/v1/login` - Login and get access token
- `GET /api/v1/health` - Health check endpoint
