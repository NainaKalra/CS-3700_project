from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route("/feed")
def feed():
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