from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Connect DB
def get_db():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )

# Home → Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            return redirect("/dashboard")
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

# Sign up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_pw),
            )
            db.commit()
            flash("Account created! Please login.", "success")
            return redirect("/")
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "danger")

    return render_template("signup.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template("dashboard.html", employees=employees)

# Add employee
@app.route("/add", methods=["GET", "POST"])
def add_employee():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        position = request.form["position"]
        salary = request.form["salary"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)",
            (name, position, salary),
        )
        db.commit()
        return redirect("/dashboard")

    return render_template("add_employee.html")

# Edit employee
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form["name"]
        position = request.form["position"]
        salary = request.form["salary"]
        cursor.execute(
            "UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s",
            (name, position, salary, id),
        )
        db.commit()
        return redirect("/dashboard")

    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()
    return render_template("edit_employee.html", employee=employee)

# Delete employee
@app.route("/delete/<int:id>")
def delete_employee(id):
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    db.commit()
    return redirect("/dashboard")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
