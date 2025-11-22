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


## Environment Variables

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Secret key for JWT encoding and decoding
- `ALGORITHM` - Algorithm for JWT encoding and decoding
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiration time in minutes

## Security

- JWT authentication
- Password hashing with bcrypt
- Email validation with email-validator
- Environment variables for sensitive data

## Database

- MySQL database integration
- SQLAlchemy ORM
- Database models for users and posts

## Testing

- Unit tests for services
- Integration tests for endpoints
- Test coverage with pytest

## Deployment

- Docker containerization
- Kubernetes deployment
- Horizontal scaling
- Load balancing

## Monitoring

- Prometheus metrics
- Grafana dashboard
- ELK stack for logging

## Documentation

- Swagger UI for API documentation
- ReDoc for API documentation
- API documentation with OpenAPI


## Follow these steps to deploy in Uroku Server
- We need Gunicorn for serving request on Heroku so install as below

```pip install gunicorn```
- Create Requirements file
- ```pip freeze > requirements.txt```
- Create Procfile with below command
```web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app```

- web: is specific to Procfile command convention that will help identify
the Heroku deployment process to start a web application with the command
next to it.
- gunicorn is the WSGI server to which we are configuring our application
to run on, with the following configuration.
- -w 4 indicates that we need our application to run on gunicorn with 4 worker processes.
- -k uvicorn.workers.UvicornWorker tells the gunicorn to run the application using uvicorn.workers.UvicornWorker worker class.
- app:app is our module main where our FastAPI() app is initialized.
- You can also specify the host and port. But Heroku will automatically figure them out