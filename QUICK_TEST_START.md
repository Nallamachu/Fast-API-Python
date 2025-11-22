# Quick Test Start Guide

## 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

## 2. Run All Tests

```bash
pytest
```

Expected output:
```
tests/test_services.py::TestUserServices::test_get_user_by_email_found PASSED
tests/test_services.py::TestUserServices::test_get_user_by_email_not_found PASSED
...
======================== 41 passed in X.XXs ========================
```

## 3. Generate Coverage Report

```bash
pytest --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see:
- Line-by-line coverage
- Coverage percentage per file
- Missing lines that need testing

## 4. Run Specific Tests

```bash
# Run only unit tests
pytest tests/test_services.py -v

# Run only integration tests
pytest tests/test_endpoints.py -v

# Run a specific test class
pytest tests/test_services.py::TestUserServices -v

# Run a specific test
pytest tests/test_services.py::TestUserServices::test_create_user_success -v
```

## 5. Verbose Output

```bash
pytest -v
```

Shows each test name and result individually.

## Test Structure

```
D:\Practice\Python\Fast-API-Python\
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                  # Pytest settings
├── .coveragerc                 # Coverage configuration
├── requirements-test.txt       # Test dependencies
├── tests/
│   ├── __init__.py
│   ├── test_services.py        # Unit tests (20 tests)
│   └── test_endpoints.py       # Integration tests (21 tests)
├── TESTING.md                  # Detailed testing guide
├── TEST_SUMMARY.md             # Test suite overview
└── QUICK_TEST_START.md         # This file
```

## What Gets Tested

### Services (Unit Tests)
- User creation and authentication
- Password hashing and verification
- JWT token generation
- Post CRUD operations
- Authorization checks

### Endpoints (Integration Tests)
- User registration
- Login and authentication
- Post creation, retrieval, update, deletion
- Error handling
- Input validation

## Common Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest --cov=.` | Show coverage in terminal |
| `pytest --cov=. --cov-report=html` | Generate HTML coverage report |
| `pytest tests/test_services.py` | Run only unit tests |
| `pytest tests/test_endpoints.py` | Run only integration tests |
| `pytest -k "test_create"` | Run tests matching pattern |
| `pytest --tb=short` | Short traceback format |

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'pytest'`
- **Solution**: Run `pip install -r requirements-test.txt`

**Issue**: `No tests ran`
- **Solution**: Make sure you're in the project root directory

**Issue**: Tests fail with database errors
- **Solution**: The tests use a temporary SQLite database, so no setup needed

**Issue**: Coverage report not generated
- **Solution**: Run `pytest --cov=. --cov-report=html` and check for errors

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements-test.txt`
2. ✅ Run tests: `pytest`
3. ✅ Generate coverage: `pytest --cov=. --cov-report=html`
4. ✅ View report: Open `htmlcov/index.html`
5. ✅ Read detailed guide: See `TESTING.md`
