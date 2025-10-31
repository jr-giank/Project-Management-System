from functools import wraps
from flask import request, jsonify

ROLE_HEADER = 'X-User-Role'

def manager_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        role = request.headers.get(ROLE_HEADER, '').strip().lower()
        if role != 'manager':
            return jsonify({'error': 'manager role required'}), 403
        return func(*args, **kwargs)
    return wrapper


