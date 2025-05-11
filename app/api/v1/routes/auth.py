from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
)
import logging
import json

from flasgger import swag_from
from marshmallow import ValidationError

from app.api.db import db
from app.api.utils.create_jwt_identity import create_jwt_identity
from app.api.utils.send_mail import schedule_email
from app.api.v1.models.customer import Customer
from app.api.v1.models.supplier import Supplier
from app.api.v1.models.user import User
from app.api.v1.schemas.user import RegisterSchema, LoginSchema
from app.api.db.redis import add_jti_to_blocklist
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.v1.services.send_mail import EmailService

logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new user with role (customer or supplier) and return JWT tokens.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string', 'enum': ['customer', 'supplier']},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'age': {'type': 'integer', 'minimum': 18},
                    'phone_number': {'type': 'string'},
                    'address': {'type': 'string'}
                },
                'required': ['username', 'email', 'password', 'role', 'first_name',
                            'last_name', 'age', 'phone_number', 'address']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                '$ref': '#/definitions/SuccessResponse'
            }
        },
        400: {
            'description': 'Invalid input or email/username already exists',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        }
    }
})
def register():
    """Register a new user with validated data and return JWT tokens."""
    logger.info("Registration attempt initiated")

    try:
        data = request.get_json()
        email = data.get('email', 'unknown')
        logger.debug(f"Registration attempt for email: {email}")

        # Validate request data using RegisterSchema
        schema = RegisterSchema()
        try:
            validated_data = schema.load(data)
            logger.debug("User registration data validated successfully")
        except ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return error_response(400, f"Invalid input data: {e.messages}")

        # Create new user
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])

        # Create role-specific record
        role_model = None
        if validated_data['role'] == 'customer':
            role_model = Customer(
                user=user,  # SQLAlchemy will handle the relationship
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                age=validated_data['age'],
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                address=validated_data['address']
            )
        elif validated_data['role'] == 'supplier':
            role_model = Supplier(
                user=user,  # SQLAlchemy will handle the relationship
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                age=validated_data['age'],
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                address=validated_data['address']
            )
        else:
            # This should never happen because of schema validation, but as a safeguard:
            logger.error(f"Invalid role specified: {validated_data['role']}")
            return error_response(400, "Invalid role specified")

        try:
            db.session.add(user)
            db.session.add(role_model)
            db.session.commit()
            logger.info(f"User registered successfully: {user.email} (ID: {user.id}, Role: {user.role})")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error during user creation: {str(e)}")
            return error_response(500, "Database error occurred")

        # Create JWT identity and tokens
        try:
            identity_str = create_jwt_identity(user)
            access_token = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)
            logger.debug(f"JWT tokens generated for user: {user.email}")
        except Exception as e:
            logger.error(f"Error generating JWT tokens: {str(e)}")
            return error_response(500, "Error generating authentication tokens")

        # Send welcome email
        EmailService.send_welcome_email(user, validated_data['first_name'])

        logger.info(f"Registration complete for user: {user.email}")
        return success_response(201, "User registered successfully", {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    except Exception as e:
        logger.critical(f"Unexpected error in registration process: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Log in a user and return JWT tokens.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'},
                    'refresh_token': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Invalid input data',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        },
        401: {
            'description': 'Invalid credentials',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        }
    }
})
def login():
    """Log in a user with validated credentials and return JWT tokens."""
    logger.info("Login attempt initiated")

    try:
        data = request.get_json()
        email = data.get("email", "unknown")
        logger.debug(f"Login attempt for email: {email}")

        # Validate request data using LoginSchema
        schema = LoginSchema()
        try:
            validated_data = schema.load(data)
            logger.debug("Login data validated successfully")
        except ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return error_response(400, f"Invalid input data: {str(e)}")

        # Check user credentials
        user = User.query.filter_by(email=validated_data['email']).first()
        if not user or not user.check_password(validated_data['password']):
            logger.warning(f"Login failed: Invalid credentials for email: {email}")
            return error_response(401, "Invalid credentials")

        # Create JWT identity and tokens
        try:
            identity_str = create_jwt_identity(user)
            access_token = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)
            logger.info(f"Login successful for user: {email} (ID: {user.id})")
        except Exception as e:
            logger.error(f"Error generating JWT tokens: {str(e)}")
            return error_response(500, "Error generating authentication tokens")

        return success_response(200, "Login successful", {
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    except Exception as e:
        logger.critical(f"Unexpected error in login process: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/logout", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'description': 'Logout a user by blacklisting their token.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token (access token) for authentication. Format: Bearer <access_token>'
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully logged out'
        },
        500: {
            'description': 'Error processing logout',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        }
    }
})
def logout():
    """Logout a user by blacklisting their JWT token."""
    try:
        current_user = get_jwt_identity()
        user_email = json.loads(current_user).get("email", "unknown") if isinstance(current_user, str) else "unknown"
        logger.info(f"Logout attempt for user: {user_email}")

        jwt_data = get_jwt()
        jti = jwt_data["jti"]

        try:
            add_jti_to_blocklist(jti)
            logger.info(f"Token blacklisted successfully for user: {user_email}")
            return success_response(200, "Successfully logged out", {})
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return error_response(500, "Error processing logout")

    except Exception as e:
        logger.critical(f"Unexpected error in logout process: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@swag_from({
    'tags': ['Authentication'],
    'description': 'Refresh the access token using a valid refresh token.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token (refresh token) for authentication. Format: Bearer <refresh_token>'
        }
    ],
    'responses': {
        200: {
            'description': 'Access token refreshed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Error refreshing token',
            'schema': {
                '$ref': '#/definitions/ErrorResponse'
            }
        }
    }
})

def refresh():
    """Refresh an access token using a valid refresh token."""
    try:
        current_user = get_jwt_identity()
        user_email = json.loads(current_user).get("email", "unknown") if isinstance(current_user, str) else "unknown"
        logger.info(f"Token refresh attempt for user: {user_email}")

        try:
            access_token = create_access_token(identity=current_user)
            logger.info(f"Access token refreshed successfully for user: {user_email}")
            return success_response(200, "Access token refreshed successfully", {
                "access_token": access_token
            })
        except Exception as e:
            logger.error(f"Error generating new access token: {str(e)}")
            return error_response(500, "Error refreshing access token")

    except Exception as e:
        logger.critical(f"Unexpected error in token refresh process: {str(e)}")
        return error_response(500, "An unexpected error occurred")