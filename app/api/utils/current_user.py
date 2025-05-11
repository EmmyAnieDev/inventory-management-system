from flask_jwt_extended import get_jwt_identity
import json
import logging

logger = logging.getLogger(__name__)


class CurrentUser:
    """Helper class to handle JWT user information."""

    @staticmethod
    def get_identity():
        """Get the current user's identity information as a dictionary."""
        identity = get_jwt_identity()
        # Handle both string JSON and direct dictionary formats
        if isinstance(identity, str):
            try:
                return json.loads(identity)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse identity as JSON: {identity}")
                return {"id": identity}
        return identity

    @staticmethod
    def get_current_user_id():
        """
        Get the current user's ID from JWT identity.
        Handles both 'user_id' and 'id' keys, and converts string IDs to integers.
        """
        identity = CurrentUser.get_identity()
        # Try to get user_id first, then fall back to id
        user_id = identity.get('user_id') or identity.get('id')
        # Convert to integer if it's a string
        if isinstance(user_id, str):
            try:
                return int(user_id)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert user_id to int: {user_id}")
        return user_id

    @staticmethod
    def get_role():
        """Get the current user's role from JWT identity."""
        role = CurrentUser.get_identity().get('role')
        logger.debug(f"Current user role: {role}")
        return role

    @staticmethod
    def check_role(allowed_roles):
        """Check if the current user has one of the allowed roles."""
        if isinstance(allowed_roles, str):
            allowed_roles = [allowed_roles]
        return CurrentUser.get_role() in allowed_roles

    @staticmethod
    def can_access_resource(resource_type, resource_id, owner_field='user_id'):
        """
        Check if current user can access a specific resource.

        This method:
        1. Gets the resource by its ID (from URL)
        2. Checks if the current user has permission to access it
           (either as admin or because they own it)

        Args:
            resource_type: The model class of the resource
            resource_id: The ID of the resource to check (from URL)
            owner_field: The field name linking to the user ID (default: 'user_id')

        Returns:
            tuple: (resource object or None, error message or None)
        """
        # Get the current user's ID from token
        current_user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        logger.debug(
            f"Access check: user ID={current_user_id}, role={role}, resource={resource_type.__name__} ID={resource_id}")

        # First, get the resource by its ID
        resource = resource_type.get_by_id(resource_id)

        # If resource doesn't exist, return not found
        if not resource:
            logger.warning(f"Resource not found: {resource_type.__name__} ID={resource_id}")
            return None, "Resource not found"

        # Admin can access any resource
        if role == 'admin':
            logger.debug(f"Admin access granted for {resource_type.__name__} ID={resource_id}")
            return resource, None

        # Regular users can only access their own resources
        # Get the resource owner's user ID
        resource_owner_id = getattr(resource, owner_field, None)

        # Ensure both IDs are integers for comparison if possible
        try:
            current_user_id_int = int(current_user_id) if current_user_id is not None else None
            resource_owner_id_int = int(resource_owner_id) if resource_owner_id is not None else None

            logger.debug(f"Comparing: current_user_id={current_user_id_int}, resource_owner={resource_owner_id_int}")

            if current_user_id_int == resource_owner_id_int:
                logger.debug(
                    f"Access granted: User {current_user_id} owns resource {resource_type.__name__} ID={resource_id}")
                return resource, None
        except (ValueError, TypeError):
            # If conversion fails, try direct comparison
            logger.debug(
                f"Integer conversion failed, trying direct comparison: {current_user_id} == {resource_owner_id}")
            if current_user_id == resource_owner_id:
                return resource, None

        logger.warning(
            f"Access denied: User {current_user_id} doesn't own resource {resource_type.__name__} ID={resource_id}")
        return None, "Access denied"