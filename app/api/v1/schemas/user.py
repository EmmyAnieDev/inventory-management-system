from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "First name is required."}
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "Last name is required."}
    )
    email = fields.Email(
        required=True,
        error_messages={"required": "Email is required.", "invalid": "Invalid email address."}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        error_messages={"required": "Password is required."}
    )

    @validates("email")
    def validate_email_domain(self, value):
        if "@" not in value or not value.endswith(".com"):
            raise ValidationError("Email must contain '@' and end with '.com'")



class LoginSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required."})
    password = fields.String(required=True, validate=validate.Length(min=6), error_messages={"required": "Password is required."})
