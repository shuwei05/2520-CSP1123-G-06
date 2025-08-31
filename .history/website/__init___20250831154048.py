from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_Name = "database.db"

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_database(app):
    if not path.exists('website/' + DB_Name):
        with app.app_context():
            db.create_all()
            print('Created Database!')
    else:
        print('Database already exists.')



def create_app():
    app  = Flask(__name__)
    app.config['SECRET_KEY'] = 'MINI IT'

    # Upload Photos
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'static/uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Database
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.root_path, DB_Name)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Note, User
    with app.app_context():
        db.create_all()  

    create_database(app)

    return app
