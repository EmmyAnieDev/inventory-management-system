swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Inventory Management System API",
        "description": """A RESTful API for tracking inventory levels through incoming supplier orders (stock additions) and outgoing customer orders (stock reductions), with multi-currency support.""",
        "version": "1.0.0"
    },
    "definitions": {
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "status_code": {"type": "integer"},
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Operation successful"},
                "data": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "usd_price": {"type": "number", "example": 100.0},
                                "naira_price": {"type": "number", "example": 75000.0}
                            }
                        },
                        {
                            "type": "string",
                            "example": "some string response"
                        }
                    ]
                }
            }
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "status_code": {"type": "integer"},
                "success": {"type": "boolean", "example": False},
                "message": {"type": "string", "example": "Invalid request"},
                "data": {"type": "null", "example": None}
            }
        }
    }
}
