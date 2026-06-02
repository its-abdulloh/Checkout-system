from flask import Flask, render_template, request, redirect, session
import sqlite3


app = Flask(__name__)
app.secret_key = "fabdk_07"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add",methods=["GET","POST"])
def add():
    if request.method == "POST":
        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()

        barcode = request.form.get("barcode")
        name = request.form.get("name")
        price = request.form.get("price")
        stock = request.form.get("stock")

        try:
            cursor.execute("""
                INSERT INTO products (barcode,name,price,stock)
                VALUES(?,?,?,?)
                """,
                (
                    barcode,
                    name,
                    price,
                    stock
                )
            )
            conn.commit()
            session["success"] = True
        
        except sqlite3.IntegrityError:
            conn.rollback()
            session["failed"] = True
        
        finally:
            conn.close()

        return redirect("/add")

    success = session.pop("success",None)
    failed = session.pop("failed",None)

    return render_template("add.html",success=success,failed=failed)
        

@app.route("/checkout",methods=["GET","POST"])
def checkout():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if "cart" not in session:
        session["cart"] = {}

    if request.method =="POST":
        barcode = request.form.get("barcode")
        product = cursor.execute("SELECT id, name, price, stock FROM products WHERE barcode = ?",(barcode,)).fetchone()

        if product:
            cart = session["cart"]

            product_id = str(product["id"])
            if product_id in cart:
                cart[product_id]["quantity"]+=1
                return redirect("/checkout")
            else:
                cart[product_id] = {
                    "name":product["name"],
                    "price":product["price"],
                    "stock":product["stock"],
                    "quantity":1
                }
                session["cart"] = cart
                return redirect("/checkout")
        else:
            return render_template("checkout.html",error = "Mahsulot topilmadi!")

    total = 0
    cart = session["cart"]
    if cart:
        for product in session["cart"].values():
            total += product["price"]*product["quantity"]

    conn.close()

    return render_template("checkout.html",cart = cart.values(),total=total)


# @app.route("/sell",methods=["POST"])
# def sell():
