from app.api.db import db
from app.api.v1.models.base import BaseModel


class Stock(BaseModel):
    __tablename__ = 'stocks'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    available_quantity = db.Column(db.Integer, nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)