from functools import wraps
from flask import request, jsonify, current_app
import jwt
import datetime as dt

def generate_token(user_id: str):
    payload = {
        "sub": user_id,
        "iat": dt.datetime.utcnow(),
        "exp": dt.datetime.utcnow() + dt.timedelta(hours=4),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=current_app.config["JWT_ALGO"])
    return token

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=[current_app.config["JWT_ALGO"]],
            )
            request.user_id = payload["sub"]
        except jwt.PyJWTError:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)

    return wrapper
