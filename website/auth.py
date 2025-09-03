from flask import Blueprint ,  render_template ,request , flash ,redirect, url_for , current_app
from .models import User , Stall , Product
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db   
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import random

auth = Blueprint('auth',__name__)

@auth.route("/map", methods=["GET"])
def map_page():
    seller_coordinates = db.session.query(Stall.latitude,Stall.longitude).all()
    coordinates = []
    for coordinate in seller_coordinates:
        coordinates.append(list(coordinate))
    return render_template("map.html",coordinates=coordinates)


@auth.route('/Usign', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        password1 = request.form.get('password1') 
        password2 = request.form.get('password2')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use another one.', category='error')
            return render_template('Ssign.html', text='Signup Page')

        if len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(user_name) < 4:
            flash('Username must be greater than 3 characters', category='error')   
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')    
        else:
            new_user = User(email=email, user_name=user_name, password1=generate_password_hash(password1,method='pbkdf2:sha256')) 
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
            # Ensure user is added to the database with format given

        
        pass
    return render_template('Usign.html', text='Signup Page')

@auth.route('/Ssign', methods=['GET', 'POST'])
def Ssignup():
    if request.method == 'POST':
        stallname = request.form.get('stallname','')
        stallowner = request.form.get('stallowner','')
        email = request.form.get('email','')
        password1 = request.form.get('password1','') 
        password2 = request.form.get('password2','')
        openhour_str = request.form.get('openhour', '00:00')
        closehour_str = request.form.get('closehour', '00:00')

        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")


        openhour = datetime.strptime(openhour_str, "%H:%M").time()
        closehour = datetime.strptime(closehour_str, "%H:%M").time()

        prof_file = request.files.get("prof_pic")
        bg_file = request.files.get("bg_pic")

        prof_filename = None
        bg_filename = None

        if prof_file and prof_file.filename != "":
            prof_filename = secure_filename(prof_file.filename)
            prof_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], prof_filename))

        if bg_file and bg_file.filename != "":
            bg_filename = secure_filename(bg_file.filename)
            bg_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], bg_filename))

        existing_stall = Stall.query.filter_by(email=email).first()
        if existing_stall:
            flash('Email already registered. Please use another one.', category='error')
            return render_template('Ssign.html', text='Signup Page')

        existing_location = Stall.query.filter_by(latitude=latitude,longitude=longitude).first()
        if existing_location:
            flash("Same location",category="error")
            return render_template("Ssign.html",text="Signup Page")

        if len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(stallname) < 2:
            flash('Username must be greater than 3 characters', category='error')  
        elif len(stallowner) < 2: 
            flash('Stall owner name must be greater than 3 characters', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error') 
        elif openhour >= closehour:
            flash('Open hour must be earlier than close hour', category='error')
        else:
            new_stall = Stall(
            stallname=stallname,
            stallowner=stallowner,
            email=email,
            password1=generate_password_hash(password1, method='pbkdf2:sha256'),
            openhour = datetime.strptime(openhour_str, "%H:%M").time(),
            closehour = datetime.strptime(closehour_str, "%H:%M").time(),
            prof_pic=prof_filename if prof_file else None,
            bg_pic=bg_filename if bg_file else None,
            latitude=float(latitude),
            longitude=float(longitude)
            )
            db.session.add(new_stall)
            db.session.commit()
            flash('Stall Account Created!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('Ssign.html', text='Signup Page')

@auth.route('/Slogin',  methods=['GET', 'POST'])
def Slogin():
    if request.method == 'POST':
        stallname = request.form.get('stallname')
        password1 = request.form.get('password1')

        stall = Stall.query.filter_by(stallname=stallname).first()
        if stall:
            if check_password_hash(stall.password1, password1):
                flash('Stall Logged in successfully!', category='success')
                login_user(stall, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Stallname does not exist.', category='error')
    return render_template('Slogin.html', text='Login Page')

@auth.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password1 = request.form.get('password1')

        user = User.query.filter_by(user_name=user_name).first()
        if user:
            if check_password_hash(user.password1, password1):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template('login.html', text='Login Page')


@auth.route('/role')
def role():
    return render_template('role.html', text='Role')

@auth.route('/admin' , methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_name = request.form.get('admin_name')
        admin_password = request.form.get('admin_password')

        if admin_name == 'admin' and admin_password == 'admin123':
            flash('Admin logged in successfully!', category='success')
            return redirect(url_for('auth.admin'))
        else:
            flash('Invalid admin credentials, try again.', category='error')
    return render_template('admin.html', text='Admin Page')

@auth.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', text='About Us')

@auth.route('/logout') 
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_des = request.form.get('product_des')
        product_type = request.form.getlist('product_type')
        product_cuisine = request.form.getlist('product_cuisine')
        price = request.form.get('price')
        product_file = request.files.get('product_pic')

        product_filename = None

        if product_file and product_file.filename != "":
            product_filename = secure_filename(product_file.filename)
            product_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], product_filename))

        if len(product_name) < 5:
            flash('Product name must be at least 5 characters long.', category='error')
        elif len(product_des) < 10:
            flash('Product description must be at least 10 characters long.', category='error')
        elif len(product_type) == 0:
            flash('Please select at least one product type.', category='error')
        elif len(product_cuisine) == 0:
            flash('Please select at least one product cuisine.', category='error')
        elif not price or float(price) <= 0:
            flash('Please enter a valid positive price.', category='error')
        else:
            new_product = Product(
                product_name=product_name,
                product_des=product_des,
                product_type=', '.join(product_type),
                product_cuisine=', '.join(product_cuisine),
                price=float(price),
                stall_id=1,
                #stall_id=current_user.id ,
                #stallname=current_user.stallname,
                product_pic=product_filename if product_file else None
            )
            db.session.add(new_product) #
            db.session.commit()#
            return render_template('add_product.html', text='Add Product Page')  
        
        # Here you would typically save the product to the database
        flash('Product added successfully!', category='success')
        return redirect(url_for('views.home'))

    return render_template('add_product.html', text='Add Product Page')

@auth.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email = request.form.get('email')
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            return redirect(url_for('/reset_password'))
        else:
            flash('This email has not registered any account. Please register an account', category='info')
            return redirect(url_for('auth.email'))
    return render_template('email.html', text='Email Page')

@auth.route('seller-profile')
def seller_profile():
    return render_template('seller-profile.html', user=current_user)

def random_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

@auth.route("/spin",methods=["GET","POST"])
def food_spin():
    items = [item.product_name for item in Product.query.all()] 
    colors = [random_hex() for _ in items]
    zipFile = list(zip(items,colors))
    return render_template("spin.html",items=items,zipFile=zipFile)