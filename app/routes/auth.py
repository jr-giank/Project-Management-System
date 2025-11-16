
import jwt
from flask import Blueprint, jsonify, request, current_app

from app.models.users import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.errorhandler(Exception)
def handle_auth_errors(e):
    return jsonify({"error": str(e)}), 500

def create_auth_token(user):
    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

    jwt_secret_key = current_app.config["JWT_SECRET_KEY"]
    jwt_algorithm = current_app.config["JWT_ALGORITHM"]

    token = jwt.encode(payload, jwt_secret_key, algorithm=jwt_algorithm)
    return token

@auth_bp.route("/token", methods=["POST"])
def token():
    """
    Generate authentication token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: credentials
        description: User credentials for login
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: Password123
    responses:
      200:
        description: Token generated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                  example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      401:
        description: Invalid credentials
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid credentials
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid crecentials"}), 401
    
    token = create_auth_token(user)
    
    return jsonify({"token": token})