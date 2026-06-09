from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "restaurant_secret_key"

# ---------------- DATABASE CONNECTION ----------------

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="aparna@cse",
        database="restaurant_db"
    )

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(%s,%s,%s)
            """,
            (name, email, password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s AND password=%s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            flash("Login Successful")
            return redirect("/menu")

        flash("Invalid Email or Password")

    return render_template("login.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect("/")

# ---------------- MENU ----------------

@app.route("/menu")
def menu():

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu")

    foods = cursor.fetchall()

    conn.close()

    return render_template(
        "menu.html",
        foods=foods
    )

# ---------------- ORDER FOOD ----------------

@app.route("/order/<int:id>")
def order_food(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM menu WHERE id=%s",
        (id,)
    )

    food = cursor.fetchone()

    cursor.execute(
        """
        INSERT INTO orders
        (user_id, food_name, quantity, total, status)
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            food["food_name"],
            1,
            food["price"],
            "Pending"
        )
    )

    conn.commit()
    conn.close()

    flash("Food Ordered Successfully")

    return redirect("/menu")

# ---------------- TABLE BOOKING ----------------

@app.route("/booking", methods=["GET", "POST"])
def booking():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        table_no = request.form["table_no"]
        booking_date = request.form["booking_date"]
        guests = request.form["guests"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO bookings
            (user_id, table_no, booking_date, guests)
            VALUES(%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                table_no,
                booking_date,
                guests
            )
        )

        conn.commit()
        conn.close()

        flash("Table Booked Successfully")

        return redirect("/booking")

    return render_template("booking.html")

# ---------------- MY ORDERS ----------------

@app.route("/myorders")
def myorders():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM orders
        WHERE user_id=%s
        """,
        (session["user_id"],)
    )

    orders = cursor.fetchall()

    conn.close()

    return render_template(
        "myorders.html",
        orders=orders
    )

# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM orders")
    revenue = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=total_users,
        orders=total_orders,
        bookings=total_bookings,
        revenue=revenue if revenue else 0
    )

# ---------------- SALES REPORT ----------------

@app.route("/report")
def report():

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
        food_name,
        SUM(quantity) AS qty,
        SUM(total) AS sales
        FROM orders
        GROUP BY food_name
        """
    )

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "report.html",
        reports=reports
    )

# ---------------- ADD MENU (ADMIN) ----------------

@app.route("/add_menu", methods=["GET", "POST"])
def add_menu():

    if request.method == "POST":

        food_name = request.form["food_name"]
        category = request.form["category"]
        price = request.form["price"]
        image = request.form["image"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO menu
            (food_name, category, price, image)
            VALUES(%s,%s,%s,%s)
            """,
            (
                food_name,
                category,
                price,
                image
            )
        )

        conn.commit()
        conn.close()

        flash("Food Added Successfully")

        return redirect("/menu")

    return render_template("add_menu.html")

# ---------------- RUN APP ----------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )