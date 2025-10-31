
from app.extensions import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tasks = db.relationship('Task', back_populates='project', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"
