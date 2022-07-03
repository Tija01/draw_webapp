import os
from sqlalchemy import create_engine, text
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import time
from helpers import apology, login_required

#PATH_TO_IMAGES_DIR = '/static/images'
MYDIR = os.path.dirname(__file__)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLalchemy to use SQLite database
engine = create_engine("sqlite+pysqlite:///draw.db", echo=True, future=True)

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
    drawings = [] # List of dictionnaries used by Jinja that wil contain each drawing data

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM library WHERE user_id = :user_id"),
            {"user_id" : session["user_id"]}
            )
        for row in result:
            drawings.append({"id": row.id, "link" : row.link, "time_stamp": row.time_stamp})

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
        # Insert the drawing informations into the DB TODO
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
       # transaction_id = db.execute("INSERT INTO transactions (user_id, symbol, shares, price, time_stamp) VALUES (?, ?, ?, ?, ?)",
        #                            session["user_id"], response["symbol"], int(request.form.get("shares")), response["price"], dt_string)

        return redirect("/")

    else:
        return render_template("draw.html")


@app.route("/library")
@login_required
def library():
    """Show all published drawings"""

    # Query database for all drawings
    drawings= []
    with engine.connect() as conn:
        result = conn.execute(
        text("SELECT username, link, time_stamp FROM users AS U, library AS L WHERE U.id = L.user_id")
            )
        for row in result:
            drawings.append({"user" : row.username, 
                "link" : row.link, "time_stamp": row.time_stamp})

    return render_template("library.html", drawings=drawings)


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
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username" : request.form.get("username")}
            )
            counter = 0
            for row in result:
                counter += 1
                user_id = row.id
                password_hash = row.hash         
            if counter == 0 or not check_password_hash(password_hash, request.form.get("password")):
                return apology("account inexistant or wrong password")

        # Remember which user has logged in
        session["user_id"] = user_id

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
        #rows = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT username FROM users WHERE username = :username"),
                {"username" : request.form.get("username")}
            )
            # Ensure username does not already exist
            counter = 0
            for row in result:
                counter += 1         
            if counter > 0:
                return apology("provided username is taken")
        

        # Generate password hash and insert it to the database, remembering his id 
        password_hash = generate_password_hash(request.form.get("password"))
        #username_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), password_hash)
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users (username, hash) VALUES (:username, :hash)"),
                {"username": request.form.get("username"), "hash": password_hash }
                )
            conn.commit()
            result = conn.execute(
                text("SELECT username FROM users WHERE username = :username"),
                {"username" : request.form.get("username")}
            )
            for row in result:
                username_id = row.username

        # log user and keep him logged in
        session["user_id"] = username_id

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")

# Save drawing as a jpeg file then TODO add url to the database
@app.route('/image', methods=['POST'])
@login_required
def image():
    '''Save image file in the server and insert the link to the database'''
    
    # Save drawings as jpg at ./images
    i = request.files['image']  # get the image
    f = ('%s.jpeg' % time.strftime("%Y%m%d-%H%M%S"))
    # i.save('%s/%s' % (PATH_TO_IMAGES_DIR, f))
    i.save(os.path.join(MYDIR, 'images/', f))
    
    link = "images/" + str(f)
    # Add images url to the database
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO library (user_id, link, time_stamp) VALUES (:user_id, :link, :time_stamp)"),
            {"user_id": session["user_id"], "link": link, 
            "time_stamp": str(time.strftime("%Y%m%d-%H%M%S"))})
        conn.commit()

    return redirect("/")