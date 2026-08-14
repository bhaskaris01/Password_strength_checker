"""
Password Strength Checker
Backend: Python + Flask + SQLite
Frontend: HTML + CSS + JavaScript

How it works (explain this in viva):
1. User submits a password from the HTML form.
2. Flask route /check receives it.
3. We run 5 rule-based checks using regex (length, uppercase,
   lowercase, digit, special character) -> each passed rule = 1 point.
4. We look up the password in a SQLite table of common/weak passwords.
   If found, it is force-classified as "Weak" no matter the score.
5. Based on total score (0-5) we classify as Weak / Medium / Strong.
6. Result is sent back to the frontend as JSON and shown on screen.
"""

import re
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "passwords.db"


# ---------- DATABASE SETUP ----------
def init_db():
    """Create the common_passwords table and seed it with well-known weak passwords."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS common_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT UNIQUE NOT NULL
        )
    """)

    # A small seed list of commonly leaked / weak passwords.
    common_list = [
        "123456", "password", "123456789", "12345678", "12345",
        "qwerty", "abc123", "password1", "111111", "123123",
        "admin", "letmein", "welcome", "iloveyou", "monkey",
        "dragon", "football", "1234567", "000000", "qwerty123"
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO common_passwords (password) VALUES (?)",
        [(p,) for p in common_list]
    )

    conn.commit()
    conn.close()


def is_common_password(password: str) -> bool:
    """Check the SQLite table for an exact (case-insensitive) match."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM common_passwords WHERE LOWER(password) = LOWER(?)",
        (password,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ---------- CORE STRENGTH-CHECK LOGIC ----------
def check_password_strength(password: str) -> dict:
    checks = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"[0-9]", password)),
        "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password)),
    }

    score = sum(checks.values())  # 0 to 5
    common = is_common_password(password)

    if common:
        strength = "Weak"
        reason = "This is a commonly used / leaked password."
    elif score <= 2:
        strength = "Weak"
        reason = "Too short or missing several character types."
    elif score in (3, 4):
        strength = "Medium"
        reason = "Decent, but could use more variety or length."
    else:
        strength = "Strong"
        reason = "Good length and character variety."

    return {
        "password_length": len(password),
        "checks": checks,
        "score": score,
        "max_score": 5,
        "is_common": common,
        "strength": strength,
        "reason": reason,
    }


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    password = data.get("password", "") if data else ""

    if not password:
        return jsonify({"error": "Password cannot be empty"}), 400

    result = check_password_strength(password)
    return jsonify(result)


if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
