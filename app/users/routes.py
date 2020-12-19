from flask import Blueprint

users = Blueprint("Users", __name__)

@users.route("/", methods=["GET", "POST"])
def index():
    return "HELLO WORLD!"