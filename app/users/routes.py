from flask import Blueprint, render_template, url_for, redirect, flash, request
from app import db, bcrypt
from app.models import User, Product, Category
from flask_login import current_user, login_user, login_required, logout_user
from app.users.forms import (
    SignUpForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    ChangePassword,
    ChangeName,
    DeleteAccount,
)
from app.users.utils import send_reset_email


users = Blueprint("users", __name__)


@users.route("/", methods=["GET", "POST"])
def index():
    return render_template("layout.html")


@users.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    else:
        user_by_name = User.query.filter_by(name=form.name.data).first()
        user_by_email = User.query.filter_by(email=form.email.data).first()
        if user_by_name:
            flash("The user with this name already exists!", "danger")
        if user_by_email:
            flash("The user with this email already exists!", "danger")
    return render_template('signup.html', title='Sign Up', form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')   # args is a dict
            flash('Successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('users.index'))                                                                       
        else:
            flash('Login unsuccessful. Please check your email address and password and try again', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("users.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = ChangePassword()
    change_name = ChangeName()
    del_account = DeleteAccount()
    if form.validate_on_submit() and form.submit1.data:
        user = current_user
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.add(user)
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("users.account"))
    if change_name.validate_on_submit() and change_name.submit2.data:
        if not User.query.filter_by(name=change_name.new_name.data).first():
            user = current_user
            user.name = change_name.new_name.data
            db.session.add(user)
            db.session.commit()
            flash("Your name has been changed!", "success")
        else:
            flash("This username is already taken. Please choose another one", "danger")
        return redirect(url_for("users.account"))
    if del_account.validate() and del_account.submit3.data:
        user = current_user
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been deleted. Hope to see you again!", "success")
        return redirect(url_for("users.signup"))
    return render_template("account.html", form=form,
                           change_name=change_name, del_account=del_account)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("users.main"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)


@users.route("/products", methods=["GET", "POST"])
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)


@users.route("/products/phones", methods=["GET", "POST"])
def phones():
    find_phones = Product.query.filter_by(category="Phones").all()
    return render_template("phones.html", find_phones=find_phones)


@users.route("/products/laptops", methods=["GET", "POST"])
def laptops():
    find_laptops = Product.query.filter_by(category="Laptops").all()
    return render_template("laptops.html", find_laptops=find_laptops)


@users.route("/cart", methods=["GET", "POST"])
def cart():
    return render_template("cart.html")