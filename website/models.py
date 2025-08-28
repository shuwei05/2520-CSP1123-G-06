from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password1 = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Stall(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    stallname = db.Column(db.String(150), unique=True, nullable=False)
    stallowner = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password1 = db.Column(db.String(150), nullable=False)
    openhour = db.Column(db.Time, nullable=False)
    closehour = db.Column(db.Time, nullable=False)
<<<<<<< HEAD
    profile_picture = db.Column(db.String(200), nullable=True)
    background_picture = db.Column(db.String(200), nullable=True)
=======
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float,nullable=False)
>>>>>>> 664e6004854e743194675cb7ab36bff9252a00f7
