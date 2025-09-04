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

            from .models import User, Stall
            from werkzeug.security import generate_password_hash

           
            if not User.query.filter_by(role='admin').first():
                new_admin = User(
                    user_name='admin',
                    password1=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    role='admin'
                    )
                db.session.add(new_admin)
                db.session.commit()

    else:
        print('Database already exists.')


def create_app():
    app  = Flask(__name__)
    app.config['SECRET_KEY'] = 'MINI IT'

    # Upload Photos
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Database
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, DB_Name)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    from .models import User, Stall
    
    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    

    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(int(user_id))
        if user:
            return user
    
        stall= Stall.query.get(int(user_id))
        if stall:
            return stall
        return None

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Note, User
    with app.app_context():
        db.create_all()  

    create_database(app)

    return app

def role_required(role):
    def decorator(f):
        from flask_login import current_user
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not current_user.is_authenticated:
                flash("Please log in to access this page.", category="error")
                return redirect(url_for("auth.admin"))
    
            if current_user.role != role:
                flash('Access denied. Insufficient permissions.', category='error')
                return redirect(url_for('views.home'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator