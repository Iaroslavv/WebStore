from flask import Blueprint, render_template

users = Blueprint("Users", __name__)

@users.route("/", methods=["GET", "POST"])
def index():
    return render_template("layout.html")