from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore


app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")
db = SQLAlchemy(app)
db.init_app(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
migrate = Migrate(app, db)

from app.users import routes
from app.users.routes import users
app.register_blueprint(users)


from app.models import User, Product, Comments, Category, Coupon, UserProd, Role
from app.users.admin_access import AccessView

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(app)
admin.add_view(AccessView(User, db.session))
admin.add_view(AccessView(Product, db.session))
admin.add_view(AccessView(Comments, db.session))
admin.add_view(AccessView(Category, db.session))
admin.add_view(AccessView(Coupon, db.session))
admin.add_view(AccessView(UserProd, db.session))

