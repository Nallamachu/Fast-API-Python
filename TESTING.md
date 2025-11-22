# Testing Guide

## Setup

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests with verbose output
```bash
python -m pytest -v
```

### Run with coverage
```bash
python -m pytest --cov=. --cov-report=html -v
```

### Run specific test file
```bash
python -m pytest tests/test_services.py -v
```

### Run with short output
```bash
python -m pytest -q
```

### Run tests with coverage report:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_services.py
pytest tests/test_endpoints.py
```

### Run tests with verbose output:
```bash
pytest -v
```

## Test Coverage

The project includes comprehensive test coverage:

### Unit Tests (`tests/test_services.py`):
- User creation, authentication, and retrieval
- Password verification and hashing
- JWT token creation and validation
- Post CRUD operations
- Authorization checks

**Test Classes:**
- `TestUserServices` - 6 tests for user operations
- `TestTokenServices` - 3 tests for JWT token operations
- `TestPostServices` - 11 tests for post operations

### Integration Tests (`tests/test_endpoints.py`):
- User registration and login endpoints
- Health check endpoint
- Post creation, retrieval, update, and deletion
- Authentication and authorization
- Error handling and validation

**Test Classes:**
- `TestUserEndpoints` - 4 tests for user endpoints
- `TestAuthenticationEndpoints` - 4 tests for auth endpoints
- `TestHealthEndpoint` - 1 test for health check
- `TestPostEndpoints` - 12 tests for post endpoints

## Test Fixtures

The `conftest.py` provides reusable fixtures:

- **`test_db`** - Temporary SQLite database for testing (session-scoped)
- **`db_session`** - Database session for each test (function-scoped)
- **`client`** - FastAPI test client with overridden dependencies
- **`test_user`** - Pre-created test user with email "test@example.com"
- **`test_post`** - Pre-created test post owned by test_user
- **`auth_token`** - Valid JWT token for authentication as test_user

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
# On Windows
start htmlcov/index.html

# On macOS
open htmlcov/index.html

# On Linux
xdg-open htmlcov/index.html
```

The coverage report shows:
- Line coverage for all modules
- Missing lines that need testing
- Coverage percentage by file

## Test Statistics

- **Total Unit Tests**: 20
- **Total Integration Tests**: 21
- **Total Test Cases**: 41
- **Coverage Configuration**: `.coveragerc`
- **Pytest Configuration**: `pytest.ini`

## Key Testing Features

1. **Isolated Database**: Each test runs against a temporary SQLite database
2. **Dependency Injection**: Database and authentication dependencies are overridden for testing
3. **Async Support**: Full support for async/await test functions
4. **Comprehensive Error Cases**: Tests cover success paths and error scenarios
5. **Authorization Testing**: Tests verify proper access control for post operations
6. **Token Validation**: Tests verify JWT token creation and validation

## Running Tests in CI/CD

For continuous integration pipelines:
```bash
pytest --cov=. --cov-report=xml --cov-report=term-missing -v
```

This generates:
- XML coverage report for CI tools
- Terminal output with missing lines
- Verbose test output for debugging
