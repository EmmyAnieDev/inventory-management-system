from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from app.api.db import db

jwt = JWTManager()
mail = Mail()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    ma.init_app(app)


    with app.app_context():
        db.create_all()

    return app