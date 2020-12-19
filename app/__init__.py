from flask import Flask


app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")

from app.users import routes
from app.users.routes import users
app.register_blueprint(users)