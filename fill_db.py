from app import app, db, bcrypt
from app.models import User, Category, Product, Coupon, Role
from PIL import Image
import os
import secrets


def create_tables():
    """Create db tables."""

    db.create_all()


def add_user():
    """Register a user on a website and add to tb."""

    password = "password"
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name="Iaroslav", email="yaroslaw.bulimov@yandex.ru",
                password=hashed_password)
    role = Role(name="user")
    db.session.add(user)
    user.roles.append(role)
    db.session.commit()


def add_admin():
    password = "admin"
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name="Admin", email="admin.admin@yandex.ru", password=hashed_password)
    role = Role(name="admin")
    db.session.add(user)
    user.roles.append(role)
    db.session.commit()

# do not need now
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics/iphone.jpg', picture_fn)
    form_picture.save(picture_path)
    #   compress pics to save memory
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def add_products():
    """Add phones and laptops to db."""

    phone1 = Product(product_name="Iphone", summary="New model of Iphone", category="Phones",
                      description="It has come out on the market this winter and deserves attention!",
                      product_amount=10, price=550, picture='iphone.jpg')
    phone2 = Product(product_name="Xiaomi", summary="New model of Xiaomi", category="Phones",
                      description="It has come out on the market this winter and deserves attention!",
                      product_amount=10, price=550, picture='iphone.jpg')

    laptop1 = Product(product_name="Ipad", summary="New model of Ipad", category="Laptops",
                      description="It has come out on the market this winter and deserves attention!",
                      product_amount=12, price=660, picture='ipad.jpg')
    laptop2 = Product(product_name="Xiaomi Ipad", summary="New model of Xiaomi Ipad", category="Laptops",
                      description="It has come out on the market this winter and deserves attention!",
                      product_amount=12, price=660, picture='ipad.jpg')
    db.session.add(phone1)
    db.session.add(phone2)
    db.session.add(laptop1)
    db.session.add(laptop2)
    db.session.commit()


def add_categories():
    """Add categories to db."""

    phones = Category(category_name="Phones")
    laptops = Category(category_name="Laptops")
    db.session.add(phones)
    db.session.add(laptops)
    db.session.commit()
    find_phone_cat = Product.query.filter_by(category="Phones").all()
    find_laptop_cat = Product.query.filter_by(category="Laptops").all()
    phones.product_cat.extend(find_phone_cat)
    laptops.product_cat.extend(find_laptop_cat)
    db.session.commit()

def add_coupon():
    """Add coupon code."""
    coupon_code = Coupon(coupon="GETCOUPON")
    db.session.add(coupon_code)
    db.session.commit()

if __name__ == "__main__":
    create_tables()
    add_user()
    add_admin()
    add_products()
    add_categories()
    add_coupon()