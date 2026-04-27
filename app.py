import os
import json
from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models.user import User
from models.post import Post 
from models.database import db
from models.user_service import UserService
from models.session_manager import SessionManager, login_required
from models.post_service import PostService
app = Flask(__name__)
app.secret_key = "techyeah"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Create tables and test within app context
with app.app_context():
    db.create_all()
    
   

# upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','mp4','mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/feed")
def feed():
    # Using the new OOP method instead of direct query
    posts = Post.get_feed_posts()  # Clean and polymorphic!
    posts_data = [post.to_feed_dict() for post in posts]
    return render_template("feed.html", posts=posts_data)

#Function is binded to the route

@app.route("/createProfile", methods=['GET','POST'])
def create_profile():
    if request.method == 'GET':
        return render_template('create_profile.html')
    
    username = request.form['username']
    role = request.form['role']
    
    user = UserService.create_user(username, role)
    if user:
        return redirect(url_for('login'))
    return redirect(url_for('create_profile'))

@app.route("/profile")
@login_required
def profile():
    user_id = SessionManager.get_current_user_id()
    profile_data = UserService.get_user_profile(user_id)

    if not profile_data:
        flash("User not found")
        return redirect(url_for('login'))
    
    return render_template("profile.html", **profile_data)

@app.route("/createPost", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        file = request.files.get('image')
        text = request.form.get('text')
        user_id = session.get('user_id')
        
        if not user_id:
            flash("Please log in to create a post")
            return redirect(url_for('login'))
        
        # Use the service
        new_post, errors = PostService.create_post(user_id, text, file, app.config['UPLOAD_FOLDER'])
        
        if errors:
            for error in errors:
                flash(error)
            return render_template("create_post.html")
        
        flash("Post created successfully!")
        return redirect(url_for("feed"))
    
    return render_template("create_post.html")

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    login_name = request.form['username']
    user = UserService.authenticate_user(login_name)

    if user:
        SessionManager.set_user_session(user.id)
        return redirect(url_for('profile'))
    else:
        flash("Username not found!")
        return render_template("login.html")

@app.route("/editProfile", methods=["GET", "POST"])
def editProfile():
    return render_template("EditProfile.html")


if __name__ =="__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)