from flask import Blueprint, render_template, url_for, redirect
from app import db, bcrypt, login_manager
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from app.users.forms import SignUpForm, LoginForm


users = Blueprint("users", __name__)

@users.route("/", methods=["GET", "POST"])
def index():
    return render_template("layout.html")

@users.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated():
        return redirect(url_for("users.index"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been successfully created!", "success")
    return render_template("signup.html", form=form)



@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated():
        return redirect(url_for("users.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('users.index'))
        else:
            flash('Login unsuccessful. Please check your email address and password and try again', 'danger')
    return render_template("login.html", form=form)