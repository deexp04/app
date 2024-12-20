from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache

mail = Mail()
db = SQLAlchemy()
cache = Cache()
api = Api(prefix='/api')
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()