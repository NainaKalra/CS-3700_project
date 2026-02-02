import os
from flask import Flask, redirect, url_for, render_template, request
from werkzeug.utils import secure_filename
from flask import Flask, redirect, url_for, render_template, request
from datetime import datetime

app = Flask(__name__)

# upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/feed")
def feed():
    posts_data = [
        {"username": "power_lifter", "content": "New PR today! 200kg Squat. Let's go!", "time": "12 MINS AGO", "type": "workout"},
        {"username": "fit_2012", "content": "Consistency is key. 30 days challenge done.", "time": "2 HOURS AGO", "type": "body"},
        {"username": "muscle_meals", "content": "Chicken and broccoli never tasted better.", "time": "5 HOURS AGO", "type": "food"}
    ]
    return render_template("feed.html", posts=posts_data)
    # 'posts' naam se data bhej rahe hain kyunki feed.html mein 'posts' likha hai
    return render_template("feed.html", posts=posts_data)

#Function is binded to the route
@app.route("/createProfile")
def create_profile():
    return render_template("create_profile.html")

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

        return render_template("create_post.html", image_url=image_url, text=text)
    else:
        return render_template("create_post.html")

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

if __name__ =="__main__":
    app.run(debug=True)