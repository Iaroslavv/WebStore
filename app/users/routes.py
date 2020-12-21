from flask import Blueprint, render_template, url_for, redirect, flash, request
from app import db, bcrypt
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from app.users.forms import SignUpForm, LoginForm


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
def account():
    pass