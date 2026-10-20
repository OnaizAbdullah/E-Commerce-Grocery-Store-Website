from flask import Flask, render_template, session, redirect, url_for, g, request
from database import get_db, close_db
from forms import RegistrationForm, LoginForm, FeedbackForm, AdminForm, AddForm, RemoveForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from functools import wraps

#Admin login:
#Admin_id: Admin456
#Password: AdminAccount234

app = Flask(__name__)
app.config["SECRET_KEY"] = "1111"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.teardown_appcontext(close_db)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None and g.admin is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

@app.before_request
def admin_logged_in_user():
    g.admin = session.get("admin_id", None)

def admin_login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.admin is None:
            return redirect(url_for("admin"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/")
@app.route("/welcome")
def index():
    return render_template("index.html")

@app.route("/items",methods= ["GET","POST"])
def items():
    db = get_db()
    items = db.execute("""SELECT * FROM items;""").fetchall()
    return render_template("items.html", items=items)

@app.route("/item/<int:product_id>")
def item(product_id):
    db = get_db()
    item = db.execute("""SELECT * FROM items
                      WHERE product_id = ?;""",(product_id,)).fetchone()
    return render_template("item.html", item=item)

@app.route("/cart")
@login_required
def cart():
    if "cart" not in session:
        session["cart"] = {}
    prices = {}
    names = {}
    
    total = 0
    db = get_db()
    for product_id in session["cart"]:
        item = db.execute("""SELECT * FROM items
                          WHERE product_id = ?;""", (product_id,)).fetchone()
        
        name = item["name"]
        names[product_id] = name
        price = item["price"]
        prices[product_id] = session["cart"][product_id] * price
        total += price * session["cart"][product_id]
        

    return render_template("cart.html", cart=session["cart"], names=names, prices=prices, total=round(total,2))


@app.route("/admin_view", methods=["GET","POST"])
@admin_login_required
def view_items():
    db = get_db()
    items = db.execute("""SELECT * FROM items;""").fetchall()
    return render_template("items.html", items=items)

@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    db = get_db()
    item = db.execute("""SELECT * FROM items
                          WHERE product_id = ?;""", (product_id,)).fetchone()

    if "cart" not in session:
        session["cart"] = {}
    if product_id in session["cart"]:
        session["cart"][product_id] += 1
    else:
        session["cart"][product_id] = 1


    return redirect(url_for("cart"))

@app.route("/clear_cart")
@login_required
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("cart"))

@app.route("/done")
@login_required
def done():
    prices = {}
    names = {}
    total = 0
    db = get_db()
    for product_id in session["cart"]:
        item = db.execute("""SELECT * FROM items
                          WHERE product_id = ?;""", (product_id,)).fetchone()
        
        name = item["name"]
        names[product_id] = name
        price = item["price"]
        prices[product_id] = session["cart"][product_id] * price
        total += price * session["cart"][product_id]
    return render_template("receipt.html" , cart=session["cart"], names=names, prices=prices, total=round(total,2), done=True)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()
    message = ""
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        password2 = form.password2.data
        if password != password2:
            form.password.errors.append("Password is not correct")
        else:
            db = get_db()
            conflict = db.execute("""SELECT * FROM users
                                WHERE user_id = ?;""", (user_id,)).fetchone()
            if conflict is not None:
                form.user_id.errors.append("User id is already taken")
            else:
                db.execute("""INSERT INTO users(user_id,password)
                        VALUES(?,?);""",(user_id, generate_password_hash(password)) )
                db.commit()
                return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/add_item", methods=["GET","POST"])
@admin_login_required
def add_item():
    form = AddForm()
    if form.validate_on_submit():
        item = form.item.data
        price = form.price.data
        category = form.category.data
        db = get_db()
        conflict = db.execute("""SELECT * FROM items
                              WHERE name = ?""",(item,)).fetchone()
        if conflict is not None:
            form.item.errors.append("Item is already in the store")
        else:
            new_item = db.execute("""INSERT INTO items(name,price,type)
                                VALUES(?,?,?)""",(item,price,category))
            db.commit()
            return render_template("add_item.html", form=form, message="Successfully added new item!")
    return render_template("add_item.html",form=form)

@app.route("/remove_item", methods=["GET","POST"])
@admin_login_required
def remove_item():
    form = RemoveForm()
    if form.validate_on_submit():
        remove_item = form.remove_item.data
        db = get_db()
        conflict = db.execute("""SELECT * FROM items
                              WHERE name = ?""",(remove_item,)).fetchone()
        if conflict is None:
            form.remove_item.errors.append("This item does not exist in the store")
        else:
            new_item = db.execute("""DELETE FROM items
                                  WHERE name= ?""",(remove_item,))
            db.commit()
            return render_template("remove_item.html", form=form, message="Successfully removed this item!")
    return render_template("remove_item.html",form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        matching_user = db.execute("""SELECT * FROM users
                              WHERE user_id = ?;""", (user_id,)).fetchone()
        if matching_user is None:
            form.user_id.errors.append("Unknown user id")
        elif not check_password_hash(matching_user["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = user_id
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/admin", methods=["GET","POST"])
def admin():
    form = AdminForm()

    if form.validate_on_submit():
        admin_id = form.admin_id.data
        password = form.password.data
        db = get_db()
        matching_admin = db.execute("""SELECT * FROM admins
                              WHERE admin_id = ?;""", (admin_id,)).fetchone()
        if matching_admin is None:
            form.admin_id.errors.append("Unknown admin account")
        elif not check_password_hash(matching_admin["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["admin_id"] = admin_id
            return redirect(url_for("index"))
    return render_template("admin.html", form=form)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin_logout")
@admin_login_required
def admin_logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/feedback",  methods=["GET","POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        response = form.feedback.data
        db = get_db()
        feedback = db.execute("""INSERT INTO feedback(feedback_text)
                              VALUES(?)""",(response,))
        db.commit()
        return render_template("thanks.html", message = "Thank you for your feedback!")
    return render_template("feedback.html", form=form)

@app.route("/view_feedback")
@admin_login_required
def view_feedback():
    db = get_db()
    view_feedback = db.execute("""SELECT * FROM feedback""").fetchall()
    return render_template("view_feedback.html", view_feedback = view_feedback)

"""
Websites Used:
https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html - learned about length parameter in WTForms validation
https://stackoverflow.com/questions/68230545/how-to-style-wtform-fields-using-custom-css-classes - Used to learn about how to style WTForms buttons in CSS
https://unsplash.com/ - Used to get images
"""