from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("feed.html")

@app.route("/createProfile")
def post():
    return render_template("create_profile.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/createPost")
def create_post():
    return render_template("create_post.html")

if __name__ =="__main__":
    app.run(debug=True)