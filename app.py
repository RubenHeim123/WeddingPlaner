import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
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
 

"""
Deletes a checklist item with the specified check_id.

Parameters:
- check_id (int): The id of the checklist item to be deleted.

Returns:
- Flask Response: A response object that redirects to the "/checklist" page.
"""
@app.route("/delete_checklist/<int:check_id>", methods=["POST"])
@login_required
def delete_checklist(check_id):
    try:
        cur.execute("DELETE FROM checklist WHERE id = ?", (check_id,))
    except Exception as e:
        return apology(f"{e}")
    return redirect("/checklist")


"""
Add a new checklist item to the database.

Parameters:
    None

Returns:
    redirect: A redirect to the "/checklist" page if the checklist item was successfully added.
    apology: An apology message if an error occurred during the insertion of the checklist item into the database.

Raises:
    None
"""
@app.route("/add_checklist", methods=["POST"])
@login_required
def add_checklist():
    item = request.form.get("item")
    if not item:
        return apology("Enter an item")
    try:
        cur.execute("INSERT INTO checklist (item, wedding_id, completed) VALUES (?,?,?)", (item, session["wedding_id"], False))
        db.commit()
    except Exception as e:
        return apology(f"{e}")
    return redirect("/checklist")


    """
    Updates the check status of a checklist item.

    Parameters:
    check_id (int): The ID of the checklist item to update.

    Returns:
    None
    """
@app.route("/update_check/<int:check_id>", methods=["POST"])
@login_required
def update_check(check_id):
    try:
        is_checked = cur.execute("SELECT completed FROM checklist WHERE id = ? AND wedding_id = ?", (check_id, session["wedding_id"])).fetchone()[0]
        if is_checked == 0:
            cur.execute('UPDATE checklist SET completed = 1 WHERE id = ? AND wedding_id = ?', (check_id,session["wedding_id"]))
        else:
            cur.execute('UPDATE checklist SET completed = 0 WHERE id = ? AND wedding_id = ?', (check_id,session["wedding_id"]))
        db.commit()
        return redirect("/checklist")
    except Exception as e:
        return apology(f"{e}")



"""
Retrieves a checklist from the database for a specific wedding.

Parameters:
    None

Returns:
    A rendered template for the checklist.html page, containing the retrieved checklist.

Raises:
    Exception: If there is an error executing the SQL query.
"""
@app.route("/checklist", methods=["GET"])
@login_required
def checklist():
    try:
        checklist = cur.execute("SELECT * FROM checklist WHERE wedding_id = ?", (session["wedding_id"],)).fetchall()
    except Exception as e:
        return apology(f"{e}")
    return render_template("checklist.html", checklist=checklist)


"""
Delete a transaction with the given ID.

Parameters:
    tr_id (int): The ID of the transaction to be deleted.

Returns:
    str: A message indicating the success or failure of the deletion.

Raises:
    Exception: If there is an error while deleting the transaction.

Redirects:
    /budget: If the transaction is successfully deleted.
"""
@app.route("/delete_tr/<int:tr_id>", methods=["POST"])
@login_required
def delete_tr(tr_id):
    try:
        cur.execute("DELETE FROM transactions WHERE id = ?", (tr_id,))
    except Exception as e:
        return apology(f"{e}")
    return redirect("/budget")


"""
Adds a new transaction to the database.

Parameters:
    None

Returns:
    None
"""
@app.route("/add_tr", methods=["POST"])
@login_required
def add_transaction():
    date = request.form.get("date")
    description = request.form.get("description")
    amount = request.form.get("amount")
    transaction_type = request.form.get("transaction_type")
    if not date or not transaction_type or not amount:
        return apology("Enter all fields")
    if not amount.isdigit():
        return apology("Amount must be a number")
    amount = int(amount)
    try:    
        cur.execute("INSERT INTO transactions (date, description, amount, wedding_id, transaction_type) VALUES (?,?,?,?,?)", (date, description, amount, session["wedding_id"] ,transaction_type))
        db.commit()
    except Exception as e:
        return apology(f"{e}")
    return redirect("/budget")


"""
Retrieves the budget information for a wedding.

Returns:
    A rendered HTML template with the budget details.
"""
@app.route("/budget", methods=["GET"])
@login_required
def budget():
    try:
        transactions = cur.execute("SELECT * FROM transactions WHERE wedding_id = ? GROUP BY date", (session["wedding_id"],)).fetchall()

        income_sum = sum(tr[3] for tr in transactions if tr[2] == 'income')

        expenses_sum = sum(tr[3] for tr in transactions if tr[2] == 'expenses')

        balance = income_sum - expenses_sum
    except Exception as e:
        return apology(f"{e}")
    return render_template("budget.html", transactions=transactions, income_sum=income_sum, expenses_sum=expenses_sum, balance=balance)


"""
Retrieve the number of guests who have RSVPed for the wedding.

Returns:
    int: The number of guests who have RSVPed.

Raises:
    Exception: If there is an error executing the database query.
"""
@app.route("/get_rsp_number", methods=["GET"])
@login_required
def get_rsp_number():
    try:
        rsp_number = cur.execute("SELECT COUNT(*) FROM guest WHERE rsvp_checkbox = 1 AND wedding_id = ?", (session["wedding_id"],)).fetchone()[0]
        return jsonify(rsp_number)
    except Exception as e:
        return apology(f"{e}")


"""
Updates the RSVP status of a guest.

Parameters:
    guest_id (int): The ID of the guest whose RSVP status needs to be updated.

Returns:
    None

Raises:
    Exception: If there is an error while updating the RSVP status.
"""
@app.route('/update_rsvp/<int:guest_id>', methods=['POST'])
@login_required
def update_rsvp(guest_id):
    try:
        is_checked = cur.execute("SELECT rsvp_checkbox FROM guest WHERE id = ?", (guest_id,)).fetchone()[0]
        if is_checked == 1:
            cur.execute('UPDATE guest SET rsvp_checkbox = 0 WHERE id = ?', (guest_id,))
        else:
            cur.execute('UPDATE guest SET rsvp_checkbox = 1 WHERE id = ?', (guest_id,))
        db.commit()
        return redirect("/guest")
    
    except Exception as e:
        return apology(f"{e}")
    

"""
Deletes a guest from the database.

Parameters:
    guest_id (int): The ID of the guest to be deleted.

Returns:
    None

Raises:
    Exception: If an error occurs while deleting the guest.

Redirects:
    /guest: After successfully deleting the guest.

Decorators:
    @app.route("/delete_guest/<int:guest_id>", methods=["POST"])
    @login_required
"""
@app.route("/delete_guest/<int:guest_id>", methods=["POST"])
@login_required
def delete_guest(guest_id):
    try:
        cur.execute("DELETE FROM guest WHERE id = ?", (guest_id,))
    except Exception as e:
        return apology(f"{e}")
    return redirect("/guest")


"""
Adds a guest to the database.

This function is called when a POST request is made to the "/add_guest" endpoint. It requires the user to be logged in.

Parameters:
    None

Returns:
    - If both the `first_name` and `last_name` parameters are missing, it returns an apology message.
    - If the guest is successfully added to the database, it redirects the user to the "/guest" endpoint.
    - If an error occurs during the database insertion, it returns an apology message with the error details.
"""
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


"""
Retrieves the list of guests for a specific wedding and displays them on the guest page.

Parameters:
    None

Returns:
    render_template: A Flask function that renders the guest.html template with the following arguments:
        - guests: A list of dictionaries containing guest information retrieved from the database.
        - guest_number: An integer representing the total number of guests for the wedding.
        - rsp_number: An integer representing the number of guests who have RSVP'd for the wedding.
"""
@app.route("/guest", methods=["GET"])
@login_required
def guests():
    try:
        guests = cur.execute("SELECT * FROM guest WHERE wedding_id = ?", (session["wedding_id"],)).fetchall()
        rsp_number = cur.execute("SELECT * FROM guest WHERE rsvp_checkbox = 1 AND wedding_id = ?", (session["wedding_id"],)).fetchall()
    except Exception as e:
        return apology(f"{e}")
    return render_template("guest.html", guests=guests, guest_number=len(guests), rsp_number=len(rsp_number))


"""
Updates a wedding project with the provided information.

Parameters:
- None

Returns:
- None
"""
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


"""
Renders the project page for a specific wedding.

Parameters:
- project_id (int): The ID of the project.

Returns:
- render_template (function): The rendered template for the project page.
"""
@app.route("/project/<project_id>")
@login_required
def project(project_id):
    try:
        wedding = cur.execute("SELECT * FROM wedding WHERE id = ?", (project_id,)).fetchone()
        session["wedding_id"] = wedding[0]
    except Exception as e:
        return apology(f"{e}")
    return render_template("project.html", wedding=wedding)


"""
Create a new project.

This function is the route handler for the '/new_project' endpoint. It is decorated with the '@app.route' decorator, which specifies the URL path and the HTTP methods that this route should respond to. It is also decorated with the '@login_required' decorator, which ensures that only authenticated users can access this route.

Parameters:
- None

Returns:
- If the request method is 'POST' and all the required fields are provided, it inserts a new record into the 'wedding' table of the database with the provided title, bride name, groom name, date, location, and the current user's ID. It then retrieves the inserted record from the database and stores the wedding ID in the session. Finally, it renders the 'project.html' template with the retrieved wedding record as the context.
- If the request method is not 'POST', it renders the 'new_project.html' template.

Throws:
- If the request method is 'POST' and the 'title' field is not provided, it raises an 'apology' exception with the error message 'No title'.
- If the request method is 'POST' and neither the 'bride_name' nor the 'groom_name' fields are provided, it raises an 'apology' exception with the error message 'Fill out a bride or a groom name'.
- If any database error occurs during the insertion of the new record, it raises an exception with the error message.

Note:
- This function assumes that the following variables are defined and have the expected values:
    - 'app' is the Flask application object.
    - 'request' is the Flask request object.
    - 'apology' is a function that renders an error page with an apology message.
    - 'cur' is the database cursor object.
    - 'db' is the database connection object.
    - 'session' is the Flask session object.
    - 'render_template' is a function that renders a template with the provided context.

Example usage:
- To create a new project, make a POST request to the '/new_project' endpoint with the required form fields.
- To view the new project form, make a GET request to the '/new_project' endpoint.

"""
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


"""
Retrieves all weddings associated with the logged-in user from the database and
renders the index.html template with the retrieved weddings.

Returns:
    str: The rendered HTML content of the index.html template.
"""
@app.route("/")
@login_required
def index():
    weddings = cur.execute("SELECT * FROM wedding WHERE user_id = ?", (session["user_id"],)).fetchall()
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

        old_user = cur.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        # Ensure username exists and password is correct
        if len(old_user) != 3 or not check_password_hash(
            old_user[2], old_password
        ):
            return apology("invalid username and/or password", 403)

        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            (generate_password_hash(new_password),
            old_user[0])
        )

        return redirect("/")
    else:
        return render_template("changepassword.html")

    