from flask import Flask, jsonify
from flasgger import Swagger, swag_from

from app.api.db import db
from app.api.db.redis import jti_in_blocklist
from app.api.swagger_definitions import swagger_template
from config import Config
from app.extensions import jwt, mail, ma, migrate


def create_app():
    app = Flask(__name__)
    Swagger(app, template=swagger_template)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Register JTI blocklist checker
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti_in_blocklist(jti)


    # Register Flask blueprints
    from app.api.v1.routes import auth
    app.register_blueprint(auth.bp)

    # Health check endpoint
    @app.route('/', methods=['GET'])
    @swag_from({
        'tags': ['Health Check'],
        'responses': {
            200: {
                'description': 'API status',
                'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}
            }
        }
    })
    def server_check():
        return jsonify({
            'message': 'Inventory Management API is running',
            'version': '1.0.0',
            'status': 'healthy'
        }), 200

    return app
