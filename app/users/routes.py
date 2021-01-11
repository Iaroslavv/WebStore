from flask import Blueprint, render_template, url_for, redirect, flash, request
from app import db, bcrypt
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from app.users.forms import (
    SignUpForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    ChangePassword,
    ChangeName,
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # hashing a password
        user = User(name=form.name.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
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
    if form.submit1.data and form.validate_on_submit():
        user = current_user
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.add(user)
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("users.account"))
    if change_name.submit2.data and change_name.validate_on_submit():
        user = current_user
        user.name = change_name.new_name.data
        db.session.add(user)
        db.session.commit()
        flash("Your name has been changed!", "success")
        return redirect(url_for("users.account"))
    return render_template("account.html", form=form, change_name=change_name)


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
