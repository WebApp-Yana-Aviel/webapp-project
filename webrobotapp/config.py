import os

# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))
devDB =  os.path.join(basedir, 'dev_app.db')
producDB=os.path.join(basedir, 'produc_app.db')
testDB = os.path.join(basedir, 'testing_app.db')

class Config(object):
    """
    Base configuration class. Contains default configuration settings + configuration settings applicable to all environments.
    """
   
    WTF_CSRF_ENABLED = True

    # Settings applicable to all environments
    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')
    # Static Assets
    STATIC_FOLDER = 'static'
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(basedir, 'static'),]
    STATIC_ROOT = os.path.join(basedir, "static")
    TEMPLATES_FOLDER = 'templates'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('xxxxx@gmail.com')
    MAIL_PASSWORD = os.environ.get('')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', default='xxxxx@gmail.com')
  

    SQLALCHEMY_TRACK_MODIFICATIONS = False
 

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + devDB

class TestingConfig(Config):
    FLASK_ENV = 'testing'
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + testDB

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + producDB
app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
