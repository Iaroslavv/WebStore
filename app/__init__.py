from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

from app.users import routes
from app.users.routes import users
app.register_blueprint(users)