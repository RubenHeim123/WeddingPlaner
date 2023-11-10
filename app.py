import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from utils import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask("__name__")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure sqlite3 Library to use SQLite database
db = sqlite3.connect("wedding.db", check_same_thread=False)
cur = db.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = request.form.get("username")
        pwd = request.form.get("password")
        # Ensure username was submitted
        if not name:
            return apology("must provide username", 403)
            

        # Ensure password was submitted
        elif not pwd:
            return apology("must provide password", 403)

        # Query database for username
        rows = cur.execute(
            "SELECT * FROM users WHERE username = ?", (name, )
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], pwd
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not name:
            return apology("Put in your username")

        if not password:
            return apology("Put in your password")

        if not confirmation:
            return apology("Put in your confirmation")

        if password != confirmation:
            return apology("Password and confirmation do not match")

        hash = generate_password_hash(password)

        try:
            cur.execute(
                "INSERT INTO users(username, hash) VALUES (?, ?)", (name, hash)
            )
            db.commit()

            # Fetch the newly inserted user's ID
            new_user_id = cur.lastrowid

            # Store the user ID in the session
            session["user_id"] = new_user_id

        except sqlite3.IntegrityError:
            return apology("Username already exists")

        return redirect("/")

    else:
        return render_template("register.html")
    
@app.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    """Change password"""
    if request.method == "POST":
        name = request.form.get("username")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not name:
            return apology("Put in your username")

        if not old_password:
            return apology("Put in your old password")

        if not new_password:
            return apology("Put in your new password")

        if not confirmation:
            return apology("Put in your confirmation")

        if new_password != confirmation:
            return apology("Password and confirmation is not the same")

        old_user = cur.execute("SELECT * FROM users WHERE username = ?", name).fetchone()

        # Ensure username exists and password is correct
        if len(old_user) != 1 or not check_password_hash(
            old_user[0][2], old_password
        ):
            return apology("invalid username and/or password", 403)

        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(new_password),
            old_user[0][0],
        )

        return redirect("/")
    else:
        return render_template("changepassword.html")

    