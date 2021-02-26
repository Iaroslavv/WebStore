from flask import (
    Blueprint,
    render_template,
    url_for, redirect,
    flash,
    request,
    current_app,
)
from app import db, bcrypt, mail
from app.models import User, Product, UserProd, Comments
from flask_login import current_user, login_user, login_required, logout_user
from app.users.forms import (
    SignUpForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordForm,
    ChangePassword,
    ChangeName,
    DeleteAccount,
    ContactForm,
    CommentForm,
)
from app.users.utils import send_reset_email
from app.users.helper_methods import find_product_by_name, del_items, del_user_acc
from flask_mail import Message


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
            next_page = request.args.get('next')
            flash('Successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('users.index'))                                                                       
        else:
            flash('Login unsuccessful. Please check your email address and password and try again', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("users.index"))


@users.route("/account/<string:username>", methods=["GET", "POST"])
@login_required
def account(username):
    form = ChangePassword()
    change_name = ChangeName()
    del_account = DeleteAccount()
    product_list = UserProd.query.filter_by(user=current_user)
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
        return del_user_acc(user)
    if request.method == "POST":
        if request.form["prod_id"]:
            prod_id = request.form.to_dict()
            return del_items(prod_id)
        return redirect(url_for("users.account"))
    return render_template("account.html", form=form,
                           change_name=change_name, del_account=del_account,
                           product_list=product_list)


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
    """Display all items."""
    products = Product.query.all()
    if request.method == "POST":
        name = request.form.to_dict()
        return find_product_by_name(name)
    return render_template("products.html", products=products)


@users.route("/products/phones", methods=["GET", "POST"])
def phones():
    """Display phones."""
    find_phones = Product.query.filter_by(category="Phones").all()
    if request.method == "POST":
        name = request.form.to_dict()
        return find_product_by_name(name)
    return render_template("phones.html", find_phones=find_phones)


@users.route("/products/laptops", methods=["GET", "POST"])
def laptops():
    """Display laptops."""
    find_laptops = Product.query.filter_by(category="Laptops").all()
    if request.method == "POST":
        name = request.form.to_dict()
        return find_product_by_name(name)
    return render_template("laptops.html", find_laptops=find_laptops)


@users.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        email = f"Email from the user: {form.email.data}"
        subject = f"Subject: {form.subject.data}"
        body = email + ". " + subject + ". " + form.message.data
        msg = Message(
            "Message from the website client.",
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[current_app.config["MAIL_GET"]],
            body=body,
        )
        mail.send(msg)
        flash("Your message has been sent!", "success")
        return redirect(url_for("users.contact"))
    return render_template("contact.html", form=form)


@users.route("/cart", methods=["POST", "GET"])
@login_required
def cart():
    """Display items in the cart."""
    user = current_user
    prices = [x.price for x in current_user.user_products]
    products_to_calculate = [x.count for x in current_user.products]
    product_list = UserProd.query.filter_by(user=user)  # I removed .all() to be able to iterate over it
    total_price = sum([int(first)*int(second) for first, second in zip(prices, products_to_calculate)])
    if request.method == "POST":
        if request.form["prod_id"]:
            prod_id = request.form.to_dict()
            return del_items(prod_id)
        return redirect(url_for("users.cart"))
    return render_template("cart.html", product_list=product_list,
                           total_price=total_price)


@users.route("/product<int:id_product>", methods=["POST", "GET"])
def product_info(id_product):
    find_product = Product.query.get_or_404(id_product)
    form = CommentForm()
    comments = Comments.query.filter_by(com_product=find_product).order_by(Comments.date_posted.desc()).all()
    user = current_user
    if request.method == "POST":
        if form.validate_on_submit():
            new_comment = Comments(content=form.content.data, author=user, com_product=find_product)
            db.session.add(new_comment)
            db.session.commit()
            flash("Your feedback has been posted!", "success")
            return redirect(url_for("users.product_info", id_product=find_product.id))

        elif "com_id" in request.form:
            get_id = request.form.to_dict()
            comment_id = get_id["com_id"]
            find_comment = Comments.query.filter_by(id=comment_id).first()
            if get_id["text"] != '':
                find_comment.content = get_id["text"]
                db.session.add(find_comment)
                db.session.commit()
                flash("Your feedback has been updated!", "success")
                return redirect(url_for("users.product_info", id_product=find_product.id))
            else:
                flash("This field cannot be empty. Please try again.", "danger")

        elif "name" in request.form:
            name = request.form.to_dict()
            return find_product_by_name(name)

        elif "del_comment" in request.form:
            get_id = request.form.to_dict()
            comment_id = get_id["del_comment"]
            find_to_del = Comments.query.filter_by(id=comment_id, author=user, com_product=find_product).first()
            db.session.delete(find_to_del)
            db.session.commit()
            flash("Your feedback has been deleted!", "success")
            return redirect(url_for("users.product_info", id_product=find_product.id))
        else:
            flash("Oops, something went wrong..", "danger")
    return render_template("product_info.html", find_product=find_product,
                           form=form, comments=comments)  
