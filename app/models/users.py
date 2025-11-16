from datetime import datetime, timezone
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

from enum import Enum
from app.extensions import db

class Role(Enum):
    manager = 'manager'
    employee = 'employee'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    @validates('password')
    def set_password(self, key, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
