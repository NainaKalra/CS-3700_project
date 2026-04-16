import os
import json
from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from models.user import User
from models.post import Post
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
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = []
    for p in posts:
        posts_data.append({
            "username": p.username,
            "content": p.caption,
            "image_url": p.image,
            "time": p.timestamp.strftime("%I:%M %p") if p.timestamp else "",
            "type": "body"
        })
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
    if 'user_id' not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    return render_template("profile.html", username=user.username, role=user.role)
    print("SESSION:", session)
    print("USER:", user)


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

            current_username = 'guest'
            if 'user_id' in session:
                user = User.query.get(session['user_id'])
                if user:
                    current_username = user.username

            new_post = Post(username=current_username, image=image_url or '', caption=text or '')
            new_post.save_to_db()
            return redirect(url_for("feed"))

        return render_template("create_post.html", image_url=image_url, text=text)
    else:
        return render_template("create_post.html")

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    login_name = request.form['username']
    user = User.query.filter_by(username = login_name).first()

    if user:
        session['user_id'] = user.id
        return redirect(url_for('profile'))
    else:
        flash("Username not found!")
        return render_template("login.html")

@app.route("/editProfile", methods=["GET", "POST"])
def editProfile():
    return render_template("EditProfile.html")


if __name__ =="__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)