from app.api.db import db
from app.api.v1.models.base import BaseModel


class OutgoingOrder(BaseModel):
    __tablename__ = 'outgoing_orders'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    quantity_order = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    total_price_to_pay = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)