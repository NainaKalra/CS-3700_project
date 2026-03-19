import os
import json
from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models.user import User
from models.database import db
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
    try:
        with open('posts.json', 'r') as f:
            posts_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        posts_data = []
    return render_template("feed.html", posts=posts_data)

#Function is binded to the route

@app.route("/createProfile", methods=['GET','POST'])
def create_profile():
    if request.method == 'GET':
        return render_template('create_profile.html')
    
    username = request.form['username']
    role = request.form['role']
    if User.query.filter_by(username = username).first():
        flash("Username already taken!")
        return redirect(url_for('create_profile'))

    new_user = User(username=username, role=role)
    new_user.save_to_db()
    flash("Profile created successfully! Please log in.")
    return redirect(url_for('login'))

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/createPost", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        file = request.files.get('image')
        text = request.form.get('text')
        image_url = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            image_url = url_for('static', filename=f'uploads/{filename}')

            # Save post to posts.json
            try:
                with open('posts.json', 'r') as f:
                    posts = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                posts = []

            new_post = {
                "username": "user",  # Change this to actual username if you have session
                "content": text,
                "image_url": image_url,
                "time": datetime.now().strftime("%I:%M %p"),
                "type": "body"
            }
            posts.insert(0, new_post)

            with open('posts.json', 'w') as f:
                json.dump(posts, f, indent=2)

            return redirect(url_for("feed"))
        
        return render_template("create_post.html", image_url=image_url, text=text)
    else:
        return render_template("create_post.html")

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    login_name = request.form['username']
    if User.query.filter_by(username = login_name).first():
        return render_template('profile.html')
    else:
        flash("Username not found!")
        return render_template("login.html")

if __name__ =="__main__":
    app.run(debug=True)