from app.api.db import db
from app.api.v1.models.base import BaseModel


class Category(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)