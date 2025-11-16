
from flask import Blueprint, jsonify, request

from app.models.users import User
from app.extensions import db
from app.auth import manager_required

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['POST'])
@manager_required
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: user
        description: The user to create
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - role
            - password
            - confirm_password
          properties:
            first_name:
              type: string
            last_name:
              type: string
            email:
              type: string
            role:
              type: string
            password:
              type: string
            confirm_password:
              type: string
    responses:
      201:
        description: User created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
                email:
                  type: string
                role:
                  type: string
                password:
                  type: string
                confirm_password:
                  type: string
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    data_fields = ['first_name', 'last_name', 'email', 'role', 'password', 'confirm_password']

    for field in data_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    if len(data['password']) < 8:
      return jsonify({"error": "Password must be at least 8 characters long"}), 400
        
    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Password do not match"}), 400
    
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        role=data['role'],
        password=data['password']
    )

    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({"error": "Email already exists"}), 400
        elif 'enum role' in str(e).lower():
            return jsonify({"error": "Invalid role"}), 400
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({
        "id": new_user.id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "role": new_user.role.value
    }), 201

@users_bp.route("/", methods=["GET"])
def list_users():
    """
    Get users
    ---
    tags:
      - Users
    responses:
      200:
        description: Users retrieved successfully
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  username:
                    type: string
                role:
                  type: string
    """

    users = User.query.all()
    return jsonify([{
      "id": user.id, 
      "first_name": user.first_name, 
      "last_name": user.last_name, 
      "email": user.email, 
      "role": user.role.value} for user in users
    ])

@users_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
                email:
                  type: string
                role:
                  type: string
      404:
        description: User not found
    """

    try:
      user_id = int(user_id)
    except ValueError:
      return jsonify({'error': 'Invalid ID format'}), 400

    user = User.query.get(user_id)
    if not user:
      return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
      "id": user.id, 
      "first_name": user.first_name, 
      "last_name": user.last_name, 
      "email": user.email, 
      "role": user.role.value
    }), 200

@users_bp.route("/<user_id>", methods=["PUT"])
@manager_required
def update_user(user_id):
    """
    Update user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
      - in: body
        name: user
        description: The user data to update
        schema:
          type: object
          properties:
            first_name:
              type: string
            last_name:
              type: string 
            email:
              type: string
            role:
              type: string
    responses:
      200:
        description: User updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
                email:
                  type: string
                role:
                  type: string
      404:
        description: User not found
    """

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    data_fields = ['first_name', 'last_name', 'email', 'role']

    for field in data_fields:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({"error": "Email already exists"}), 400
        elif 'enum role' in str(e).lower():
            return jsonify({"error": "Invalid role"}), 400
        return jsonify({"error": "Internal server error"}), 500
    
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role.value
    }), 200

@users_bp.route("/<user_id>", methods=["DELETE"])
@manager_required
def delete_user(user_id):
    """
    Delete user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
    """

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID format'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': 'User deleted successfully'}), 200