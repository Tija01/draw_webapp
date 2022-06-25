import os

#from cs50 import SQL Read SQLalchemy documentation to not use this library, add the alternative to requirements.txt
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///draw.db")

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
    """Show user drawings"""

    # Query database for user stock drawings
    drawings = db.execute("SELECT  FROM drawingss WHERE   ", session["user_id"])

    return render_template("index.html", drawings=drawings)


@app.route("/draw", methods=["GET", "POST"])
@login_required
def draw():
    """Make a drawing"""
    if request.method == "POST":
        '''# Form verifications
        if not request.form.get("symbol"):
            return apology("must provide a symbol", 403)
        '''
        # Insert the drawing informations into the DB
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        transaction_id = db.execute("INSERT INTO transactions (user_id, symbol, shares, price, time_stamp) VALUES (?, ?, ?, ?, ?)",
                                    session["user_id"], response["symbol"], int(request.form.get("shares")), response["price"], dt_string)

        return redirect("/")

    else:
        return render_template("draw.html")


@app.route("/library")
@login_required
def library():
    """Show all published drawings"""

    # Query database for all drawings
    librart = db.execute("SELECT symbol, shares, price, time_stamp FROM transactions WHERE user_id=?", session["user_id"])

    return render_template("library.html", user_history=user_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password verification", 400)

        # Require password to be of a certain length
        elif len(request.form.get("password")) < 6:
            return apology("Minimum password length is 6 characters", 400)

        # Ensure password and password verification match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("both passwords entered must match", 400)

        # Query database for username
        rows = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("provided username is taken")

        # Generate password hash and insert it to the database, remembering his id
        password_hash = generate_password_hash(request.form.get("password"))
        username_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), password_hash)

        # log user and keep him logged in
        session["user_id"] = username_id

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")