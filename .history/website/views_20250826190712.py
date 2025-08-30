from flask import Blueprint
from flask import render_template
from flask_login import login_required, current_user

views = Blueprint('views',__name__)

@views.route('/aboutus')
@login_required
def home():
    return render_template('aboutus.html', text='Home Page')
