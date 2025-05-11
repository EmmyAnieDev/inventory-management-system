from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.user import User
from app.api.v1.models.customer import Customer
from app.api.v1.models.supplier import Supplier


class RegisterSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=1, max=80),
        error_messages={"required": "Username is required."}
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={"required": "Password is required."}
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(['customer', 'supplier']),
        error_messages={"required": "Role is required.", "invalid": "Role must be 'customer' or 'supplier'."}
    )
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

    @validates("email")
    def validate_email_unique(self, value, **kwargs):
        """Check if email is unique across all relevant tables."""
        if User.query.filter_by(email=value).first() or \
           Customer.query.filter_by(email=value).first() or \
           Supplier.query.filter_by(email=value).first():
            raise ValidationError("Email already exists")

    @validates("username")
    def validate_username_unique(self, value, **kwargs):
        """Check if username is unique in User table."""
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already exists")


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address."
        }
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={"required": "Password is required."}
    )