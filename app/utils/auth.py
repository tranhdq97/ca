import jwt
from flask import request, jsonify
from functools import wraps
from app.config import Config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get the token from the Authorization header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        try:
            # Decode the token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            request.user = data  # Attach user data to the request
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated
