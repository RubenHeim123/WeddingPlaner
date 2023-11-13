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


@app.route('/update_rsvp/<int:guest_id>', methods=['POST'])
@login_required
def update_rsvp(guest_id):
    try:
        is_checked = cur.execute("SELECT rsvp_checkbox FROM guest WHERE id = ?", (guest_id,)).fetchone()[0]
        if is_checked == 0:
            cur.execute('UPDATE guest SET rsvp_checkbox = 1 WHERE id = ?', (guest_id,))
        else:
            cur.execute('UPDATE guest SET rsvp_checkbox = 0 WHERE id = ?', (guest_id,))
        return redirect("/guest")

    except Exception as e:
        return apology(f"{e}")
    

@app.route("/delete_guest/<int:guest_id>", methods=["POST"])
@login_required
def delete_guest(guest_id):
    try:
        cur.execute("DELETE FROM guest WHERE id = ?", (guest_id,))
    except Exception as e:
        return apology(f"{e}")
    return redirect("/guest")


@app.route("/add_guest", methods=["POST"])
@login_required
def add_guest():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    if not first_name and not last_name:
        return apology("Write first and last name")

    try:
        guests = cur.execute("INSERT INTO guest (first_name, last_name, rsvp_checkbox, wedding_id) VALUES (?,?,?,?)", (first_name, last_name, 0, session["wedding_id"]))
        db.commit()
    except Exception as e:
        return apology(f"{e}")
    return redirect("/guest")
    
    
@app.route("/guest", methods=["GET"])
@login_required
def guests():
    try:
        guests = cur.execute("SELECT * FROM guest WHERE wedding_id = ?", (session["wedding_id"],)).fetchall()
        print(guests)
    except Exception as e:
        return apology(f"{e}")
    return render_template("guest.html", guests=guests)

@app.route("/change_project", methods=["POST"])
@login_required
def change_project():

    title = request.form.get("title")
    bride_name = request.form.get("bride_name")
    groom_name = request.form.get("groom_name")
    location = request.form.get("location")
    date = request.form.get("date")

    try:
        cur.execute("""
            UPDATE wedding
            SET title = ?, bride_name = ?, groom_name = ?, wedding_date = ?, location = ?
            WHERE id = ? AND user_id = ?
        """, (title, bride_name, groom_name, date, location, session["wedding_id"], session['user_id']))    
    except Exception as e:
        return apology(f"{e}")
    
    cur.execute("SELECT * FROM wedding WHERE title = ? AND bride_name = ? AND groom_name = ? AND wedding_date = ? AND location = ? AND user_id = ?", (title, bride_name, groom_name, date, location, session["user_id"]))
    result = cur.fetchone()
    session["wedding_id"] = result[0]
    return redirect(f"/project/{result[0]}")


@app.route("/project/<project_id>")
@login_required
def project(project_id):
    try:
        wedding = cur.execute("SELECT * FROM wedding WHERE id = ?", (project_id,)).fetchone()
        session["wedding_id"] = wedding[0]
    except Exception as e:
        return apology(f"{e}")
    return render_template("project.html", wedding=wedding)


@app.route('/new_project', methods=["GET", "POST"])
@login_required
def new_project():
    if request.method == "POST":
        title = request.form.get("title")
        bride_name = request.form.get("bride_name")
        groom_name = request.form.get("groom_name")
        location = request.form.get("location")
        date = request.form.get("date")

        if not title:
            return apology("No title")
        
        if not bride_name and not groom_name:
            return apology("Fill out a bride or a groom name")
        
        try:
            cur.execute("INSERT INTO wedding (title, bride_name, groom_name, wedding_date, location, user_id) VALUES (?, ?, ?, ?, ?, ?)", (title, bride_name, groom_name, date, location, session["user_id"]))
            db.commit()
        except Exception as e:
            return apology(f"{e}")

        cur.execute("SELECT * FROM wedding WHERE title = ? AND bride_name = ? AND groom_name = ? AND wedding_date = ? AND location = ? AND user_id = ?", (title, bride_name, groom_name, date, location, session["user_id"]))
        result = cur.fetchone()
        session["wedding_id"] = result[0]

        return render_template("project.html", wedding=result)
    else:
        return render_template("new_project.html")


@app.route("/")
@login_required
def index():
    weddings = cur.execute("SELECT * FROM wedding WHERE user_id = ?", (session["user_id"],)).fetchall()
    print(weddings)
    return render_template("index.html", weddings=weddings)

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

    