"""
auth.py — Signup, Login + JWT token_required decorator
"""

import re, jwt, bcrypt, datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from database import get_db

auth_bp = Blueprint("auth", __name__)


# ── Helper: JWT banana ────────────────────────────────────────────────────────

def _make_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email":   email,
        "exp":     datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


# ── Decorator: protected routes ke liye ──────────────────────────────────────

def token_required(f):
    """
    Use this on any route that needs login.
    Token Authorization header mein bhejo:
      Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"success": False, "message": "Login required"}), 401

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = {"user_id": data["user_id"], "email": data["email"]}
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Session expired, please login again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


# ── POST /api/auth/signup ─────────────────────────────────────────────────────

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Body (JSON):
      { first_name, last_name, email, password, phone?, state? }
    Returns:
      { success, token, user }
    """
    data = request.get_json(silent=True) or {}

    # Validation
    for field in ["first_name", "last_name", "email", "password"]:
        if not data.get(field, "").strip():
            return jsonify({"success": False, "message": f"'{field}' required hai"}), 400

    email = data["email"].strip().lower()
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"success": False, "message": "Valid email address daalo"}), 400

    if len(data["password"]) < 8:
        return jsonify({"success": False, "message": "Password kam se kam 8 characters ka hona chahiye"}), 400

    # Password hash
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()

    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (first_name, last_name, email, phone, state, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["first_name"].strip(),
            data["last_name"].strip(),
            email,
            data.get("phone", "").strip(),
            data.get("state", "").strip(),
            hashed,
        ))
        conn.commit()
        user_id = c.lastrowid
    except Exception as e:
        conn.close()
        if "UNIQUE" in str(e):
            return jsonify({"success": False, "message": "Yeh email already registered hai"}), 409
        return jsonify({"success": False, "message": "Server error, dobara try karo"}), 500
    finally:
        conn.close()

    return jsonify({
        "success": True,
        "token": _make_token(user_id, email),
        "user": {
            "id":         user_id,
            "first_name": data["first_name"].strip(),
            "last_name":  data["last_name"].strip(),
            "email":      email,
        },
    }), 201


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Body (JSON):
      { email, password }
    Returns:
      { success, token, user }
    """
    data  = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    pwd   = data.get("password", "")

    if not email or not pwd:
        return jsonify({"success": False, "message": "Email aur password dono required hain"}), 400

    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()

    if not user or not bcrypt.checkpw(pwd.encode(), user["password"].encode()):
        return jsonify({"success": False, "message": "Galat email ya password"}), 401

    return jsonify({
        "success": True,
        "token": _make_token(user["id"], email),
        "user": {
            "id":         user["id"],
            "first_name": user["first_name"],
            "last_name":  user["last_name"],
            "email":      user["email"],
        },
    })
