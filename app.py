from __future__ import annotations

import json
import os
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = os.environ.get("TCHAI_DATA_FILE", "storage.json")


def load_transactions() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_transactions(transactions: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as handle:
        json.dump(transactions, handle, indent=2)


def parse_iso8601(timestamp: str) -> datetime:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp)


def sort_transactions(transactions: list[dict]) -> list[dict]:
    return sorted(transactions, key=lambda tx: parse_iso8601(tx["t"]))


def validate_transaction(data: dict) -> tuple[bool, str | None]:
    required_keys = ("p1", "p2", "t", "a")
    for key in required_keys:
        if key not in data:
            return False, f"Missing field: {key}"

    if not isinstance(data["p1"], str) or not data["p1"].strip():
        return False, "p1 must be a non-empty string"
    if not isinstance(data["p2"], str) or not data["p2"].strip():
        return False, "p2 must be a non-empty string"
    if data["p1"] == data["p2"]:
        return False, "p1 and p2 must be different"

    try:
        parse_iso8601(data["t"])
    except Exception:
        return False, "t must be a valid ISO-8601 timestamp string"

    try:
        amount = float(data["a"])
    except Exception:
        return False, "a must be a number"
    if amount <= 0:
        return False, "a must be > 0"

    data["a"] = amount
    return True, None


@app.route("/transactions", methods=["POST"])
def add_transaction():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify(error="Request body must be JSON"), 400

    ok, error = validate_transaction(payload)
    if not ok:
        return jsonify(error=error), 400

    transactions = load_transactions()
    transactions.append(payload)
    transactions = sort_transactions(transactions)
    save_transactions(transactions)

    return jsonify(payload), 201


@app.route("/transactions", methods=["GET"])
def list_transactions():
    transactions = sort_transactions(load_transactions())
    return jsonify(transactions), 200


@app.route("/transactions/<person>", methods=["GET"])
def list_transactions_for_person(person: str):
    transactions = load_transactions()
    linked = [tx for tx in transactions if tx["p1"] == person or tx["p2"] == person]
    linked = sort_transactions(linked)
    return jsonify(linked), 200


@app.route("/balance/<person>", methods=["GET"])
def balance(person: str):
    transactions = load_transactions()
    received = sum(tx["a"] for tx in transactions if tx["p2"] == person)
    sent = sum(tx["a"] for tx in transactions if tx["p1"] == person)
    return jsonify(person=person, balance=received - sent), 200


if __name__ == "__main__":
    app.run(debug=True)
