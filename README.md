# Cat Charity Fund

[![CI](https://github.com/alina-milto/cat-charity-fund/actions/workflows/main.yml/badge.svg)](https://github.com/alina-milto/cat-charity-fund/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.135-green)

Async REST API for a charity fund that supports cats. Users donate money,
and the service automatically distributes donations across fundraising
projects. Superusers can export a report of funded projects to Yandex Disk.

**Stack:** Python, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic,
fastapi-users (JWT), httpx, SQLite, pytest, GitHub Actions

## Highlights

- **Automatic investment:** each new donation or project is matched with
  open ones in first-in, first-out order; fully funded items close
  automatically
- **Report to Yandex Disk:** an Excel report of closed projects, sorted by
  funding speed, uploaded through the Yandex Disk REST API with an async
  httpx client
- **95 tests** and CI that runs flake8, checks migrations against models
  and runs the tests on every pull request
- JWT authentication, required strong secret, validation of all input

## Quick start

```bash
git clone https://github.com/alina-milto/cat-charity-fund.git
cd cat-charity-fund
python -m venv venv
source venv/bin/activate        # Windows: source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET, see the comment in the file
alembic upgrade head
uvicorn app.main:app
```

Open http://127.0.0.1:8000/docs for the interactive API documentation.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Author

**Alina Milto** — [GitHub](https://github.com/alina-milto)
