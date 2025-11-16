
import jwt
from functools import wraps
from flask import request, jsonify, current_app

from app.models.users import User

def manager_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if user.role.value != 'manager':
            return jsonify({'error': 'manager role required'}), 403
        return func(user, *args, **kwargs)
    return wrapper

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token required"}), 401
        
        try:
            token = token.replace("Bearer ", "")
            payload = jwt.decode(
                token, 
                current_app.config["JWT_SECRET_KEY"], 
                algorithms=current_app.config["JWT_ALGORITHM"]
            )
            user = User.query.get(payload['id'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception:
            return jsonify({"error": "Authentication error"}), 401
        
        return func(user, *args, **kwargs)
    return wrapper