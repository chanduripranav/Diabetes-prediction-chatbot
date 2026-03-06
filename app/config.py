import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key-change-this")
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-secret-change")
    JWT_ALGO = "HS256"
