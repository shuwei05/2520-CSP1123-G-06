from flask import Blueprint ,  render_template ,request , flash ,redirect, url_for , current_app
from .models import User , Stall , Product
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db   
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import random
from website import role_required
import uuid

auth = Blueprint('auth',__name__)

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
            flash('Stall account submission created! Please wait for approval.', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('Ssign.html', text='Signup Page')

@auth.route('/Slogin',  methods=['GET', 'POST'])
def Slogin():
    if request.method == 'POST':
        stallname = request.form.get('stallname')
        password1 = request.form.get('password1')

        stall = Stall.query.filter_by(stallname=stallname).first()
        if stall:
            if not stall.approval_status:
                flash('Your stall is pending approval. Please wait for admin approval.', category='info')
                return render_template('Slogin.html', text='Login Page')
            
            if check_password_hash(stall.password1, password1):
                flash('Stall Logged in successfully!', category='success')
                login_user(stall, remember=True)
                print(f"Seller logged in: {stall.stallname}, role={stall.role}")

                return redirect(url_for('auth.seller_profile'))
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

@auth.route('/admin-login' , methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_name = request.form.get('admin_name')
        admin_password = request.form.get('admin_password')

        admin = User.query.filter_by(user_name=admin_name, role='admin').first()

        if admin:
            if check_password_hash(admin.password1, admin_password):
                flash('Admin Logged in successfully!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('auth.admin_dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Admin username does not exist.', category='error')
    

    return render_template('admin-login.html', text='Admin Page')


@auth.route('/admin_dashboard')
@role_required('admin')
def admin_dashboard():
    pending_stalls = Stall.query.filter_by(approval_status=False).all()
    return render_template('admin_dashboard.html', pending_stalls=pending_stalls)

@auth.route('/approve_stall/<int:stall_id>', methods=['POST'])
@role_required('admin')
def approve_stall(stall_id):
    stall = Stall.query.get_or_404(stall_id)
    stall.approval_status = True
    db.session.commit()
    flash(f'Stall "{stall.stallname}" has been approved.', category='success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/deny_stall/<int:stall_id>', methods=['POST'])
@role_required('admin')
def deny_stall(stall_id):
    stall = Stall.query.get_or_404(stall_id)
    db.session.delete(stall)
    db.session.commit()
    flash(f'Stall "{stall.stallname}" has been denied and removed.', category='info')
    return redirect(url_for('auth.admin_dashboard'))


@auth.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', text='About Us')

@auth.route('/forgot-password')
def forgot_password():
    return render_template('reset-password.html', text='Forgot Password')

@auth.route('/logout', method=['POST']) 
@login_required
def logout():
    print(f"Logging out user: {current_user}")
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('views.home'))

@auth.route('/add_product', methods=['GET', 'POST'])
@role_required('stall')
def add_product():

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_des = request.form.get('product_des')
        product_type = request.form.getlist('product_type')
        product_cuisine = request.form.getlist('product_cuisine')
        price = request.form.get('price')
        product_file = request.files.get('product_pic')


        if not product_name or len(product_name) < 5:
            flash('Product name must be at least 5 characters long.', category='error')
        elif not product_des or len(product_des) < 10:
            flash('Product description must be at least 10 characters long.', category='error')
        elif not product_type:   # request.form.getlist always returns a list
            flash('Please select at least one product type.', category='error')
        elif not product_cuisine:
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
                stall_id=current_user.id ,
            )

            db.session.add(new_product)
            db.session.flush()

            if product_file and product_file.filename != "":
                ext = os.path.splitext(product_file.filename)[1]
                product_filename =f"{new_product.id}{ext}"
                product_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], product_filename))
                new_product.product_pic = product_filename
                db.session.commit()

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


@auth.route("/map", methods=["GET"])
def map_page():
    seller_coordinates = db.session.query(Stall.latitude,Stall.longitude).all()
    coordinates = []
    for coordinate in seller_coordinates:
        coordinates.append(list(coordinate))
    return render_template("map.html",coordinates=coordinates)

@auth.route('/view-map')
@role_required('user')
def view_map():
    return render_template('view-map.html')

@auth.route('/menu')
@role_required('user')
def menu():
    products = Product.query.all()
    return render_template('menu.html', products=products)

@auth.route('/view-details')
@role_required('user')
def view_menu():
    products = Product.query.all()
    return render_template('view-details.html', products=products)

@auth.route('/profile')
@role_required('user')
def profile():
    return render_template('profile.html', user=current_user)

@auth.route('/seller-profile')
@role_required('stall')
def seller_profile():
    return render_template('seller-profile.html', user=current_user)

@auth.route('/stall-menu' , methods=['GET', 'POST'])
@role_required('stall')
def stall_menu():
    products = Product.query.filter_by(stall_id=current_user.id).all()
    return render_template('stall-menu.html', products=products)

@auth.route('/filter', methods=['GET', 'POST'])
@role_required('user')
def filter():
    if request.method == 'POST':
        selected_cuisines = request.form.getlist('cuisine')
        selected_types = request.form.getlist('type')

        query = Product.query

        if selected_cuisines:
            query = query.filter(
                db.or_(*[Product.product_cuisine.ilike(f'%{cuisine}%') for cuisine in selected_cuisines])
            )

        if selected_types:
            query = query.filter(
                db.or_(*[Product.product_type.ilike(f'%{ptype}%') for ptype in selected_types])
            )

        filtered_products = query.all()
        return render_template('filter.html', products=filtered_products, selected_cuisines=selected_cuisines, selected_types=selected_types)

    return render_template('filter.html', products=[], selected_cuisines=[], selected_types=[])

@auth.route("/spin",methods=["GET","POST"])
@role_required('user')
def food_spin():
    items = [{"product_name": product.product_name,"stall_name":stall.stallname,"stall_hour":f"{stall.openhour} - {stall.closehour}"}
             for product,stall in db.session.query(Product,Stall) #check for 2 database
             .join(Stall, Product.stall_id == Stall.id)
             .all()] #join the relationship
    
    color_Library = ["#FF9AA2", "#FFB7B2", "#FFDAC1","#E2F0CB", "#B5EAD7", "#C7CEEA",
                     "#F6C1C0", "#F7DAD9", "#F9E2AE","#A5DEE5", "#B4E7CE", "#D6E2F0",
                     "#FFD1DC", "#FFB3C0", "#FF95A4","#FDD7AA", "#FCE1C6", "#FAF1D9",
                     "#C9E4C5", "#A7D7C5", "#82CBB2","#A5BFF0", "#9AA7E0", "#8F90D9",
                     "#CDB4DB", "#FFC8DD", "#FFAFCC","#BDE0FE", "#A2D2FF"]
    
    colors = [color_Library[item % len(color_Library)]for item in range(len(items))]

    gradientColor = []
    degree = 360 / len(items)
    for i,color in enumerate(colors):
        start = i * degree
        end = (i + 1) * degree
        gradientColor.append(f"{color} {start}deg {end}deg")
    
    seperator = "conic-gradient("+",".join(gradientColor) + ")"
    return render_template("spin.html",items=items,seperator=seperator)
