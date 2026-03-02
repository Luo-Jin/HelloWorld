```markdown
# HelloWorld

## Flask App

A minimal Flask web application using SQLite and SQLAlchemy.

Setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

Run locally:

```bash
PYTHONPATH=. .venv/bin/python run.py
```

Run tests:

```bash
PYTHONPATH=flask_app .venv/bin/python -m pytest -q flask_app/tests
```

Usage: seeding the database
---------------------------

To populate the app database with public school data run the seeder script:

```bash
python3 seed_public_schools.py --region Auckland --limit 1000 --force
```

Adjust `--region`, `--limit`, and remove `--force` as needed.

```
