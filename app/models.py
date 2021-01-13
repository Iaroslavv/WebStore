from app import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


user_prod = db.Table("user_prod",
        db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
        db.Column("product_id", db.Integer, db.ForeignKey("product.id"))
        )


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    user_products = db.relationship("Product", secondary=user_prod,
                                    backref=db.backref("products", lazy="dynamic"))

    def get_reset_token(self, expires_sec=1800):
        serial = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return serial.dumps({"user_id": self.id}).decode("utf-8")
    
    @staticmethod
    def verify_reset_token(token) -> str:
        serial = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(token)["user_id"]
        except Exception:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(64), unique=True, nullable=False)
    summary = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(440), nullable=False)
    picture = db.Column(db.String())
    product_amount = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, default=0)
    
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    
    def __repr__(self):
        return f"Product('{self.product_name}', '{self.summary}', '{self.description}', '{self.price}')"


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(30))
    product_cat = db.relationship("Product", backref="product", lazy=True)
    
    def __repr__(self):
        return f"Product('{self.category_name}')"
