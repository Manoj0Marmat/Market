from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from market import app, db
from market.forms import LoginForm, PurchaseItemForm, RegisterForm, SellingForm
from market.model import Item, User


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/market", methods=["GET", "POST"])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellingForm()
    if request.method == "POST":
        purchased_item = request.form.get("purchased_item")
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.owner = current_user.id
                current_user.budget -= p_item_object.price
                db.session.commit()
                flash(
                    f"Congratulations! You Purchased {p_item_object.name} for {p_item_object.price}",
                    category="success",
                )
            else:
                flash(
                    f"Unfortunately, you don't have enough money to purchase {p_item_object.name}",
                    category="danger",
                )

        sell_item = request.form.get("sold_item")
        s_item_object = Item.query.filter_by(name=sell_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.owner = None
                current_user.budget += s_item_object.price
                db.session.commit()
                flash(
                    f"Congratulations! You Sold {s_item_object.name} back to market !",
                    category="success",
                )
            else:
                flash(
                    f"Somethind went wrong to selling {s_item_object.name}",
                    category="danger",
                )

        return redirect(url_for("market_page"))

    if request.method == "GET":
        item = Item.query.filter_by(owner=None)
        owned_item = Item.query.filter_by(owner=current_user.id)
        return render_template(
            "market.html",
            items=item,
            owned_item=owned_item,
            purchase_form=purchase_form,
            selling_form=selling_form,
        )


@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(
            f"Success! you are created account and logged in as:{user_to_create.username}",
            category="success",
        )
        return redirect(url_for("market_page"))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"There was error with creating a user {err_msg}", category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_user=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f"Success! you are logged in as:{attempted_user.username}",
                category="success",
            )
            return redirect(url_for("market_page"))
        else:
            flash(
                "Username and Password not match! Please Try Again", category="danger"
            )

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been log out!", category="info")
    return redirect(url_for("home_page"))
