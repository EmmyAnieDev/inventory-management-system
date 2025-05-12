from app.api.db import db
from app.api.v1.models.base import BaseModel


class IncomingOrder(BaseModel):
    __tablename__ = 'incoming_orders'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    quantity_supply = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    supply_date = db.Column(db.DateTime, nullable=False)