from flask import Flask,render_template,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_script import Manager
from flask_migrate import Migrate
from config import app_config
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_bootstrap import Bootstrap
import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app(config_name):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
   ################----
    
    Bootstrap(app)
    db.init_app(app)
    bcrypt.init_app(app)
 
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    migrate=Migrate(app, db, render_as_batch=True)

    manager=Manager(app)
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=465
    app.config['MAIL_USERNAME']='webrobotapp2021@gmail.com'
    app.config['MAIL_PASSWORD']='gdwedgjwfdihlaoh'
    app.config['MAIL_USE_TLS']=False
    app.config['MAIL_USE_SSL']=True
    mail.init_app(app)
    db.app=app

    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        #since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    from app import models
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .home import home as main_blueprint
    app.register_blueprint(main_blueprint)
      
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
        create_directories()
    
    @app.errorhandler(403)
    def forbidden(error):
       return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500
    
    @app.route('/500')
    def error():
        abort(500)

    return app


def create_directories():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    folders = ['images', 'videos']
    for folder in folders:
        try:
            os.mkdir(f'{current_dir}/static/{folder}', mode=0o777)
        except FileExistsError:
            pass
        