from app import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# a m2m table to connect relation between user and chosen products
class UserProd(db.Model):
    __tablename__ = "user_prod"
    __table_args__ = (db.UniqueConstraint("user_id", "product_id"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete="CASCADE"))
    count = db.Column(db.Integer, default=0)
    
    user = db.relationship("User", backref="products")
    product = db.relationship("Product", backref="products")
    
    def __repr__(self):
        return f"{self.count}" 


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    prod_amount = db.Column(db.Integer, default=0)
    user_products = db.relationship("Product", secondary="user_prod",
                                    lazy='dynamic', cascade="all, delete",
                                    passive_deletes=True, backref="products_user"
                                    )
    comments = db.relationship("Comments", backref="author", lazy=True)

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
    picture = db.Column(db.String(20), nullable=False)
    product_amount = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)
    category = db.Column(db.String(30), nullable=False)
    
    users = db.relationship("User", secondary="user_prod",
                            cascade="all, delete", passive_deletes=True
                            )
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    comments = db.relationship("Comments", backref="com_product", lazy=True)
    
    def __repr__(self):
        return f"('{self.product_name}', '{self.summary}', '{self.description}', '{self.price}', '{self.product_amount}')"


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    
    def __repr__(self):
        return f"Comment('{self.content}','{self.date_posted}')"


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon = db.Column(db.String(), nullable=False, default="GETCOUPON")

    def __repr__(self):
        return f"{self.coupon}"


# one2many relationship between Category and Product
class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(30))
    product_cat = db.relationship("Product", backref="product", lazy=True)
  
    def __repr__(self):
        return f"Category('{self.category_name}')"
    