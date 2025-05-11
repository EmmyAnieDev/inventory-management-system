from app.api.db import db
from app.api.v1.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = 'products'

    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.relationship('Stock', backref='product', uselist=False, lazy=True)