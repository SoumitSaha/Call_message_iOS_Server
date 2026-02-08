import firebase_admin
from firebase_admin import credentials, auth as fb_auth
from functools import wraps
from flask import request, jsonify
from .config import FIREBASE_CRED_PATH

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str) -> dict:
    return fb_auth.verify_id_token(id_token)

def require_auth(require_verified: bool = True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing Bearer token"}), 401

            token = auth_header.split("Bearer ", 1)[1].strip()
            try:
                decoded = verify_firebase_token(token)
            except Exception as e:
                return jsonify({"error": "Invalid token", "detail": str(e)}), 401

            if require_verified and not decoded.get("email_verified", False):
                return jsonify({"error": "Email not verified"}), 403

            request.firebase = decoded
            return f(*args, **kwargs)
        return wrapper
    return decorator