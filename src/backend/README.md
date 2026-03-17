# Online Judge Backend

FastAPI-based backend for the Online Judge system.

## Features

- ⚡ **FastAPI**: Modern, fast (high-performance) web framework
- 🔄 **Async SQLAlchemy**: Asynchronous ORM for database operations
- 🗄️ **SQLite/PostgreSQL**: Flexible database support
- 🔐 **JWT Authentication**: Secure token-based authentication
- 📝 **Pydantic**: Data validation using Python type hints
- 🔧 **Alembic**: Database migrations
- ✅ **Pytest**: Comprehensive testing framework

## Quick Start

### Prerequisites

- Python 3.11+
- uv (recommended) or pip

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (using uv - extremely fast!)
uv pip install -r requirements.txt -r requirements-dev.txt

# Copy environment variables
cp .env.example .env

# Edit .env and configure your settings
vim .env
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Create initial migration (if needed)
alembic revision --autogenerate -m "Initial migration"
```

### Running the Server

```bash
# Development server with auto-reload
uvicorn main:app --reload

# Or using Python directly
python main.py

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/api/docs
- Alternative docs (ReDoc): http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/          # API version 1
│   ├── core/            # Core configuration
│   │   ├── config.py   # Settings
│   │   ├── database.py # Database setup
│   │   ├── security.py # Auth utilities
│   │   └── deps.py     # Dependencies
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   └── middleware/      # Custom middleware
├── alembic/             # Database migrations
├── tests/               # Tests
├── main.py             # Application entry point
├── pyproject.toml      # Project configuration
└── requirements.txt    # Dependencies
```

## Development

### Code Quality

```bash
# Format code
black .
ruff check --fix .

# Type checking
mypy app

# Run all checks
make lint
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_health.py -v
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## API Documentation

Once the server is running, visit:
- http://localhost:8000/api/docs for interactive Swagger UI
- http://localhost:8000/api/redoc for ReDoc documentation

## Environment Variables

Key environment variables (see `.env.example` for all options):

```bash
# Application
APP_NAME="Online Judge"
DEBUG=True

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./oj.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000
```

## Switching to PostgreSQL

To use PostgreSQL instead of SQLite:

1. Start PostgreSQL (using Docker):
```bash
docker-compose up -d postgres
```

2. Update `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://oj:password@localhost:5432/oj
```

3. Run migrations:
```bash
alembic upgrade head
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT License
