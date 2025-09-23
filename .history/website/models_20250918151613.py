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
    role = db.Column(db.String(50), nullable=False,default='user')

    def get_id(self):
        return f"user-{self.id}"

class Stall(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    stallname = db.Column(db.String(150), unique=True, nullable=False)
    stallowner = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password1 = db.Column(db.String(150), nullable=False)
    openhour = db.Column(db.Time, nullable=False)
    closehour = db.Column(db.Time, nullable=False)
    prof_pic = db.Column(db.String(200), nullable=True)
    bg_pic = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float,nullable=False)
    stall_des = db.Column(db.String(200),nullable=False)
    role = db.Column(db.String(50), nullable=False,default='stall')
    location = db.Column(db.String(50),nullable=False,unique=True)
    openday =  db.Column(db.String(50),nullable=False)
    contact = db.Column(db.String(50),nullable=False,unique=True)
    instagram = db.Column(db.String(50),nullable=False)
    products = db.relationship('Product', backref='stall' , lazy=True)
    rating = db.Column(db.Float, default=0.0)
    rating_total = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)

    

    approval_status = db.Column(db.Boolean, default=False)

    def get_id(self):
        return f"stall-{self.id}"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    product_des = db.Column(db.String(500), nullable=True)
    product_cuisine= db.Column(db.String(100), nullable=False)
    product_type= db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stall_id = db.Column(db.Integer, db.ForeignKey('stall.id'), nullable=False)
    product_pic = db.Column(db.String(200), nullable=True)


class Review(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    review = db.Column(db.String(500),nullable=False)
    rating = db.Column(db.String(50),nullable=False)
    review_pic = db.Column(db.String(200),nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    stall_id = db.Column(db.Integer,db.ForeignKey('stall.id'),nullable=False)

    user = db.relationship('User', backref='reviews')


class Webreview(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    review_text = db.Column(db.String(500),nullable=False)
    review_name = db.Column(db.String(50),nullable=False)

    user = db.relationship('User', backref='webreviews')