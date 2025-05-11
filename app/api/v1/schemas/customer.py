from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.customer import Customer
from app.api.v1.models.supplier import Supplier
from app.api.v1.models.user import User


class CustomerSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "First name is required."}
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Last name is required."}
    )
    age = fields.Integer(
        required=True,
        validate=validate.Range(min=18),
        error_messages={"required": "Age is required."}
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    phone_number = fields.String(
        required=True,
        validate=validate.Length(min=10, max=20),
        error_messages={"required": "Phone number is required."}
    )
    address = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200),
        error_messages={"required": "Address is required."}
    )
    date_created = fields.DateTime(dump_only=True)

    @validates("email")
    def validate_email_unique(self, value):
        if Customer.query.filter_by(email=value).first() or \
           Supplier.query.filter_by(email=value).first() or \
           User.query.filter_by(email=value).first():
            raise ValidationError("Email already exists")