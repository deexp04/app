from datetime import timedelta

class Config(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SECRET_KEY = 'secret-key'
    
    JWT_SECRET_KEY = 'jwt-secret-key'
    JWT_COOKIE_SECURE = False
    JWT_TOKEN_LOCATION = ['headers','cookies']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_SESSION_COOKIE = False  
    JWT_ACCESS_COOKIE_EXPIRES = timedelta(hours=1)
    BUNDLE_ERRORS = True
    PROPAGATE_EXCEPTIONS = True
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = None 
    JWT_CSRF_IN_COOKIES = True  
    JWT_CSRF_COOKIE_HTTPONLY = False  
    JWT_CSRF_CHECK_FORM = True
    JWT_COOKIE_DOMAIN = '.localhost'

    MAIL_SERVER = 'smtp.gmail.com'  
    MAIL_PORT = 587  
    MAIL_USE_TLS = True  
    MAIL_USE_SSL = False  
    MAIL_USERNAME = 'deebhika04@gmail.com' 
    MAIL_PASSWORD = 'puir bbir xyon zvrz'

    CACHE_TYPE =  "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 30
    CACHE_REDIS_PORT = 6379

# import os

# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = os.getenv('MAIL_PORT', 587)
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('DEFAULT_SENDER_EMAIL', 'default_sender@example.com')

# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-email-password
# .env
