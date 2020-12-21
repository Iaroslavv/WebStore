from flask import Blueprint, render_template

users = Blueprint("Users", __name__)

@users.route("/", methods=["GET", "POST"])
def index():
    return render_template("layout.html")

@users.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")



@users.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")