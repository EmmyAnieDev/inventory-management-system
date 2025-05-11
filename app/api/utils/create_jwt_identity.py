def create_jwt_identity(user):
    """
    Create a JWT identity string from a user object.

    Args:
        user: User object with id, username, and email attributes

    Returns:
        str: JSON string containing user identity information
    """
    import json

    identity = {
        "id": str(user.id),  # Ensure ID is a string
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    return json.dumps(identity)  # Convert to a JSON string