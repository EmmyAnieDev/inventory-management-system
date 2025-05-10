from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

jwt = JWTManager()
mail = Mail()
ma = Marshmallow()
migrate = Migrate()