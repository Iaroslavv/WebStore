from app import db
from app.models import Product, UserProd
from flask_login import current_user
from flask import redirect, render_template, url_for, flash


def find_product_by_name(name):
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
