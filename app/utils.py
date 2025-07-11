from functools import wraps
from flask import session, redirect, url_for, flash

def login_verification(f):
    @wraps(f)
    def login_verification_function(*args, **kwargs): #Using decorators to allow this function to wrap around all routings.
        if 'username' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs) #Pass all arguments back to the original view of the user.
    return login_verification_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
