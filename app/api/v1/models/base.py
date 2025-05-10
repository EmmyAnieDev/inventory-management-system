from datetime import datetime
from app.api.db import db

class BaseModel(db.Model):
    """Base model for all entities with common attributes and methods"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        """Save the model instance to the database"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the model instance from the database"""
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by ID"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all instances of the model"""
        return cls.query.all()