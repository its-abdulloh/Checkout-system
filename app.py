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
        