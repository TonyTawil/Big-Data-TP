# Tchai v1

Flask API for recording transactions and querying lists and balances.

## Auteur

Veronica El Hoyek : veronica_el-hoyek@etu.u-bourgogne.fr
Antoine Tawil : antoine_tawil@etu.u-bourgogne.fr

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
flask --app app run --debug
```

Or:

```bash
python app.py
```

## API

Transaction format:

```json
{"p1":"Alice","p2":"Bob","t":"2026-01-05T14:30:00Z","a":10.5}
```

Endpoints:

- `POST /transactions` - record a transaction
- `GET /transactions` - list all transactions chronologically
- `GET /transactions/<person>` - list transactions linked to a person
- `GET /balance/<person>` - balance for a person
