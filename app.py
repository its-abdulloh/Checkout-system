from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

if not os.path.exists("store.db"):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """       
    )
    conn.commit()
    conn.close()

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

        try:
            cursor.execute("""
                INSERT INTO products (barcode,name,price)
                VALUES(?,?,?)
                """,
                (
                    barcode,
                    name,
                    price,
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
        product = cursor.execute("SELECT id, name, price FROM products WHERE barcode = ?",(barcode,)).fetchone()

        if product:
            cart = session["cart"]

            product_id = str(product["id"])
            if product_id in cart:
                cart[product_id]["quantity"]+=1
                session["cart"] = cart
                return redirect("/checkout")
            else:
                cart[product_id] = {
                    "name":product["name"],
                    "price":product["price"],
                    "quantity":1
                }
                session["cart"] = cart
                return redirect("/checkout")
        else:
            return render_template("checkout.html",error = "Mahsulot topilmadi!",cart = session["cart"])

    total = 0
    cart = session["cart"]
    if cart:
        for product in cart.values():
            total += product["price"]*product["quantity"]
    conn.close()

    return render_template("checkout.html",cart = cart,total=total)

@app.route("/clear",methods=["POST"])
def clear():
    session["cart"] = {}
    return redirect("/checkout")

@app.route("/update_quantity",methods=["POST"])
def update_quantity():
    product_id = request.form.get("product_id")
    action = request.form.get("action")

    cart = session["cart"]

    if action=="increase":
        cart[product_id]["quantity"]+=1
    elif action=="decrease":
        cart[product_id]["quantity"]-=1

        if cart[product_id]["quantity"]==0:
            del cart[product_id]

    session["cart"] = cart
    return redirect("/checkout")

@app.route("/sell",methods=["POST"])
def sell():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    cart = session["cart"]

    for product in cart.values():
        product_name = product["name"]
        price = product["price"]
        quantity = product["quantity"]
        total = price*quantity

        cursor.execute("INSERT INTO sales(product_name,price,quantity,total) VALUES(?,?,?,?)",(product_name,price,quantity,total))
    
    conn.commit()
    conn.close()

    session["cart"] = {}

    return redirect("/checkout")

@app.route("/sales")
def sales():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    

    sales = cursor.execute("SELECT product_name, price, quantity, total, datetime(sale_date, 'localtime') as sale_date FROM sales ORDER BY sale_date DESC").fetchall()

    conn.close()

    return render_template("sales.html",sales = sales)

@app.route("/products")
def products():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    query = request.args.get("q")

    if query:
        products = cursor.execute("SELECT barcode,name,price FROM products WHERE name LIKE ? ORDER BY name ASC",("%"+query+"%",)).fetchall()
    else:
        products = cursor.execute("SELECT barcode,name,price FROM products ORDER BY name ASC").fetchall()

    conn.close()

    return render_template("products.html",products = products)

    
@app.route("/edit/<barcode>", methods=["GET","POST"])
def edit(barcode):
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    if request.method == "GET":
        product = cursor.execute("SELECT name,price FROM products WHERE barcode=?",(barcode,)).fetchone()

        if not product:
            conn.close()
            return redirect("/products")

        conn.close()

        return render_template("edit.html",product=product)
    
    else:
        name = request.form.get("name")
        price = request.form.get("price")

        cursor.execute("UPDATE products SET name=?,price=? where barcode=?",(name,price,barcode))

        conn.commit()
        conn.close()

        return redirect("/products")

@app.route("/delete/<barcode>", methods=["POST"])
def delete(barcode):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    
    product = cursor.execute(
        "SELECT barcode FROM products WHERE barcode=?",
        (barcode,)
    ).fetchone()

    if not product:
        conn.close()
        return redirect("/products")

    cursor.execute("DELETE FROM products WHERE barcode=?",(barcode,))

    conn.commit()
    conn.close()
    
    return redirect("/products")


if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run()
