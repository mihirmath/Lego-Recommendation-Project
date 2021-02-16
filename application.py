# export API_KEY=pk_8051cc95e907485e85650b89a68a5b62

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import requests
import urllib.parse
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
# Add database
db = SQL("sqlite:///legosets.db")
@app.route("/favorites")
def favorites():
    favs = []
    favorites = db.execute("""SELECT DISTINCT name, price, pieces, image_url FROM legosets
                   WHERE id IN (SELECT legoset_id FROM favorites WHERE user_id=?)
                   ORDER BY price;""", session['id'])
    for favorite in favorites:
            favs.append({
                "name": favorite['name'],
                "price": usd(favorite['price']),
                "pieces": favorite['pieces'],
                "url": favorite['image_url']
            })
    return render_template("favorites.html", favorites=favorites)
@app.route("/highlight", methods=["POST"])
def highlight():
    legoId = db.execute("SELECT id FROM legosets WHERE name = ?", request.get_json(force = True)['legoset'])
    favoritesId = db.execute("INSERT INTO favorites (user_id, legoset_id) VALUES (?, ?)", session['id'], legoId[0]['id'])
    return 'OK'
@app.route("/unhighlight", methods=["POST"])
def unhighlight():
    legoId = db.execute("SELECT id FROM legosets WHERE name = ?", request.get_json(force = True)['legoset'])
    favoritesId = db.execute("DELETE FROM favorites WHERE (user_id, legoset_id) = (?, ?)", session['id'], legoId[0]['id'])
    return 'OK'
@app.route("/populars")
def populars():
    populars = []
    favorites = []
    pops = db.execute("""SELECT name, price, pieces, image_url
                        FROM favorites
                        JOIN legosets ON favorites.legoset_id=legosets.id
                        GROUP BY legoset_id
                        ORDER BY COUNT(legoset_id) DESC LIMIT 25""")

    for pop in pops:
        populars.append({
            "name": pop['name'],
            "price": usd(pop['price']),
            "pieces": pop['pieces'],
            "url": pop['image_url']
            })
    favs = db.execute("""SELECT DISTINCT(name), price, pieces, image_url FROM legosets WHERE id IN
                        (SELECT DISTINCT legoset_id
                        FROM favorites
                        JOIN legosets ON legoset_id=legosets.id WHERE user_id = ?)""", session['id'])
    for fav in favs:
        favorites.append({
            "name": fav['name'],
            "price": usd(fav['price']),
            "pieces": fav['pieces'],
            "url": fav['image_url']
        })
        print(favorites)
        if fav in pops:
            populars.remove({
                "name": fav['name'],
                "price": usd(fav['price']),
                "pieces": fav['pieces'],
                "url": fav['image_url']
                })
    return render_template("populars.html", populars=populars, favorites=favorites)
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # QUERY FOR POPULAR LEGOSETS
        # SELECT name, price, pieces, image_url FROM favorites JOIN legosets ON favorites.legoset_id=legosets.id GROUP BY legoset_id ORDER BY COUNT(legoset_id) DESC;
        budget = request.form.get("budget")
        if not budget:
            budget = 10000
        pieces_min = request.form.get("pieces_min")
        if not pieces_min:
            pieces_min = 0
        if int(pieces_min) < 0:
            flash('You must have a positive number of pieces!')
            return redirect('/')
        pieces_max = request.form.get("pieces_max")
        if not pieces_max:
            pieces_max = 5922
        if int(pieces_min) > int(pieces_max):
            flash('Your minimum pieces are larger than your max pieces!')
            return redirect('/')
        theme = request.form.get("theme")
        if not theme:
            recs = db.execute("""SELECT DISTINCT name, price, pieces, image_url FROM legosets
                                WHERE price <= ? AND pieces BETWEEN ? AND ?
                                ORDER BY price""", budget, pieces_min, pieces_max)
        else:
            recs = db.execute("""SELECT DISTINCT name, price, pieces, image_url FROM legosets
                                WHERE theme = ? AND price <= ? AND pieces BETWEEN ? AND ?
                                ORDER BY price""", theme, budget, pieces_min, pieces_max)
        recommendations = []
        for rec in recs:
            recommendations.append({
                "name": rec['name'],
                "price": usd(rec['price']),
                "pieces": rec['pieces'],
                "url": rec['image_url']
            })
        favorites = []
        if not theme:
            favs = db.execute("""SELECT DISTINCT(name), price, pieces, image_url FROM legosets WHERE id IN
                            (SELECT DISTINCT legoset_id
                            FROM favorites
                            JOIN legosets ON legoset_id=legosets.id
                            WHERE price < ? AND pieces BETWEEN ? AND ? AND user_id = ?
                            ORDER BY price)""",  budget, pieces_min, pieces_max, session['id'])
        else:
            favs = db.execute("""SELECT DISTINCT(name), price, pieces, image_url FROM legosets WHERE id IN
                            (SELECT DISTINCT legoset_id
                            FROM favorites
                            JOIN legosets ON legoset_id=legosets.id
                            WHERE theme = ? AND price < ? AND pieces BETWEEN ? AND ? AND user_id = ?
                            ORDER BY price)""",  theme, budget, pieces_min, pieces_max, session['id'])
        for fav in favs:
            favorites.append({
                "name": fav['name'],
                "price": usd(fav['price']),
                "pieces": fav['pieces'],
                "url": fav['image_url']
                })
            if fav in recs:
                recommendations.remove({
                    "name": fav['name'],
                    "price": usd(fav['price']),
                    "pieces": fav['pieces'],
                    "url": fav['image_url']
                    })
        if recommendations == []:
            populars = []
            pops = db.execute("""SELECT name, price, pieces, image_url
                                FROM favorites
                                JOIN legosets ON favorites.legoset_id=legosets.id
                                GROUP BY legoset_id
                                ORDER BY COUNT(legoset_id) DESC LIMIT 25""")

            for pop in pops:
                populars.append({
                    "name": pop['name'],
                    "price": usd(pop['price']),
                    "pieces": pop['pieces'],
                    "url": pop['image_url']
                    })
            favs = db.execute("""SELECT DISTINCT(name), price, pieces, image_url FROM legosets WHERE id IN
                                (SELECT DISTINCT legoset_id
                                FROM favorites
                                JOIN legosets ON legoset_id=legosets.id WHERE user_id = ?)""", session['id'])
            for fav in favs:
                favorites.append({
                    "name": fav['name'],
                    "price": usd(fav['price']),
                    "pieces": fav['pieces'],
                    "url": fav['image_url']
                })
                print(favorites)
                if fav in pops:
                    populars.remove({
                        "name": fav['name'],
                        "price": usd(fav['price']),
                        "pieces": fav['pieces'],
                        "url": fav['image_url']
                        })
            return render_template("popular.html", populars=populars, favorites=favorites)
        return render_template("recommendation.html", recommendations=recommendations, favorites=favorites)
    else:
        themes = []
        rows = db.execute("SELECT DISTINCT theme FROM legosets")
        for row in rows:
            themes.append({
                "theme": row['theme']
            })
        return render_template("index.html", themes=themes)

# Display a table of all the favorite legosets. If the user unfavorites a legoset --> remove it from the table
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # if the form was submitted by the user
    if request.method == "POST":
        # Check for invalid user input
        username = request.form.get("username")
        # If the user did not type in a username
        if not username:
            flash('Missing Username!')
            return redirect("/register")
        password = request.form.get("password")
        # If the user did not type in a password
        if not password:
            flash('Missing Password!')
            return redirect("/register")
        confirm_password = request.form.get("confirmation")
        # If the user did not confirm their password
        if not confirm_password:
            flash('Confirm Password!')
            return redirect("/register")
        # If the user did not confirm their password correctly
        if password != confirm_password:
            flash('Passwords Do Not Match!')
            return redirect("/register")
        # If the user's username is already in the database
        hash = generate_password_hash(password)
        checkUsername = db.execute("SELECT * FROM users WHERE username = ?", username)
        if checkUsername:
            flash('Username Already Exists!')
            return redirect("/register")
        insert = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")
    # if the form was not submitted by the user, redirect the user to register for an account
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        # Ensure username was submitted
        if not username:
            flash('Missing Username!')
            return redirect("/")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Missing Password!')
            return redirect("/")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Invalid Username/Password!')
            return redirect("/")

        # Remember which user has logged in
        session["id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

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