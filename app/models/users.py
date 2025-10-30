
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

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
