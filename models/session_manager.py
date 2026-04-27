# utils/session_manager.py
from flask import session, flash, redirect, url_for
from functools import wraps

class SessionManager:
    
    @staticmethod
    def set_user_session(user_id):
        session['user_id'] = user_id
    
    @staticmethod
    def clear_session():
        session.clear()
    
    @staticmethod
    def get_current_user_id():
        return session.get('user_id')
    
    @staticmethod
    def is_logged_in():
        return 'user_id' in session
    
    @staticmethod
    def logout():
        SessionManager.clear_session()
        flash("You have been logged out.")

# Decorator for route protection
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SessionManager.is_logged_in():
            flash("Please log in to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function