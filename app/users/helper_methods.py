from app import db
from app.models import Product, UserProd, User
from flask_login import current_user
from flask import redirect, render_template, url_for, flash
from sqlalchemy.orm.exc import StaleDataError


def find_product_by_name(name):
    """
    Add product to the cart and update counter in the association table
    as well as counter at user's table.
    """
    find_product = Product.query.filter_by(product_name=name["name"]).first()
    product_name = name["name"]
    if find_product.product_amount < 1:
        flash("This product is unavailable at the moment!", "info")
        return redirect(url_for("users.products"))
    else:
        user = current_user
        prod = UserProd.query.filter_by(user=user, product=find_product).first()
        if find_product not in user.user_products:
            user.user_products.append(find_product)
            prod = UserProd.query.filter_by(user=user, product=find_product).first()
            prod.count = 1
            user.prod_amount += 1
            find_product.product_amount -= 1
            db.session.commit()
        else:
            user.prod_amount += 1   # update total counter in user's products
            find_product.product_amount -= 1
            prod.count = prod.count + 1     # update counter in product
            db.session.commit()
        flash(f"{product_name} was successfully added to your cart!", "success")
        return redirect(url_for("users.products"))
    return render_template("products.html")


def del_items(prod_id):
    """Remove product from cart by id."""
    find_product = Product.query.filter_by(id=prod_id["prod_id"]).first()
    user = User.query.filter_by(id=current_user.id).first()
    prod = UserProd.query.filter_by(user=current_user, product=find_product).first()
    try:
        find_product.product_amount += prod.count
        user.prod_amount -= prod.count

        user.user_products.remove(find_product)
        db.session.commit()
    except StaleDataError:
        db.session.rollback()
        flash("Something went wrong. The error has been sent to the admin", "info")
        return redirect(url_for("users.cart"))
    return render_template("cart.html")
