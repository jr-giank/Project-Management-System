## Project Management System

A small Flask-based API for a management system
### Stack
- Flask, Flask-SQLAlchemy, Flask-Migrate, Flasgger (Swagger UI)
- PyTest for tests

### Prerequisites
- Python 3.10+
- pip

### 1) Setup
```bash
git clone <repo_url>
cd "Project Management System"

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env and set SECRET_KEY and DB_URL
```

Environment variables (see `env.example`):
- SECRET_KEY: Flask secret key
- DB_URL: SQLAlchemy database URI (examples below)

Examples:
- PostgreSQL: `postgresql+psycopg2://user:password@localhost:5432/db_name`

### 2) Initialize the database

Flask-Migrate:
```bash
# Run migrations
flask db upgrade
```

### 3) Run the server

Flask CLI:
```bash
flask run
```

The API will be available at `http://127.0.0.1:5000`.

Swagger UI: `http://127.0.0.1:5000/apidocs`

### Role-based access control
- Any route that modifies the database requires the header: `X-User-Role: manager`.
- Read-only (GET) routes do not require this header.

Example create project:
```bash
curl -X POST http://127.0.0.1:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "X-User-Role: manager" \
  -d '{"name":"Project #1","description":"desc"}'
```

### Running tests
```bash
pytest
```

### Documentation (Sphinx)
```bash
# Open the docs
open docs/_build/html/index.html
```


