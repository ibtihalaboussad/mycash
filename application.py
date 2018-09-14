from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import smtplib

# Configure application
app = Flask(__name__)

db = SQL("sqlite:///mycash.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

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


@app.route("/", methods=["GET", "POST"])
def home():
    """Let user sign up or log in"""
    if request.method == "POST":
        # Validation of inputs in both login and signup cases is done through javascript in template
        # Let user sign up if requests signup
        if request.form['homebutton'] == 'signup':
            # Ensure that user can be added to table which implies that used email is not already taken (because email is unique)
            result = db.execute("INSERT INTO users (name, email, hash, budget) VALUES(:name, :emaill, :hash, :budget)", name=request.form.get("firstname"), emaill=request.form.get("email"),
                            hash=generate_password_hash(request.form.get("password")), budget=request.form.get("budgetsign"))
            if not result:
                # Redirect to welcome page if email used, with javascript alert that will be caused by "boolean=1" in template
                return render_template("welcome.html", boolean=1)
            else:
                # If user sucecssfully signed up, redirect them to /input (aka logged in user's home page) with their session ID
                rows = db.execute("SELECT * FROM users WHERE email = :email",
                                  email=request.form.get("email"))
                session["user_id"] = rows[0]["id"]
                return redirect("/input")

        # Let user log in if requests login
        elif request.form['homebutton'] == 'login':
            rows = db.execute("SELECT * FROM users WHERE email = :email",
                                  email=request.form.get("email"))
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                # If not, redirect to welcome page with javascript alert that will be caused by "right=1" in template
                return render_template("welcome.html", right=1)
            # If user logs in successfully, redirect them to /input with their session ID
            session["user_id"] = rows[0]["id"]
            return redirect("/input")

    else: #if request.method == "GET":
        if session.get("user_id") is None:
            # "boolean=0" serves to initially display no alert when user uses GET and not POST
            return render_template("welcome.html", boolean=0)
        else:
            return redirect("/input")


@app.route("/input", methods=["GET", "POST"])
@login_required
def addinput():
    """Let user input past expenditure"""
    if request.method == "POST":
        # Input validation is done through javascript in template
        # If input valid, insert data about the expenditure in "spendings" table
        result = db.execute("INSERT INTO spendings (date, category, details, amount, user_id) VALUES(:date, :category, :details, :amount, :user_id)",
        date=request.form.get("day"), category=request.form.get("category"), details=request.form.get("details"), amount=request.form.get("amount"), user_id=session["user_id"])
        # Redirect to /input in case user wants to input more expenditures
        return redirect("/input")
    else: #if request.method == "GET":
        row = db.execute("SELECT * FROM users WHERE id = :id",
                                      id=session["user_id"])
        currentname = row[0]["name"]
        # Session ID allows us to retrieve name of user to display it on the page
        return render_template("input.html", name=currentname)

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Let users view and sort history of all their expenditures"""
    if request.method == "POST":
        # Generate differently-sorted SQL lists depending on sorting method user selected in form
        historylist=[]
        # Old to recent date
        if request.form.get("chosensorting") == '1':
            sorting_order="Date: old to recent"
            historylist = db.execute(
            "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY date", current_id=session["user_id"])
        # Recent to old date
        if request.form.get("chosensorting") == '2':
            sorting_order="Date: recent to old"
            historylist = db.execute(
            "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY date DESC", current_id=session["user_id"])
        # Low to high amount
        if request.form.get("chosensorting") == '3':
            sorting_order="Amount: low to high"
            historylist = db.execute(
            "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY amount", current_id=session["user_id"])
        # High to low amount
        if request.form.get("chosensorting") == '4':
            sorting_order="Amount: high to low"
            historylist = db.execute(
            "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY amount DESC", current_id=session["user_id"])
        # Sort based on category (and sort elements of the same category based on date: old to new)
        if request.form.get("chosensorting") == '5':
            sorting_order="Category"
            historylist = db.execute(
            "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY category, date", current_id=session["user_id"])

        # Get sum of all user's inputted expenditures
        totalo = db.execute(
        "SELECT details, SUM(amount) AS total FROM spendings WHERE user_id = :current_id", current_id=session["user_id"])
        # If total is none, display "0" for total in template
        if not totalo[0]["total"]:
            totalexp = 0
        else:
            totalexp = totalo[0]["total"]
        # Get user's selected sorting method for in case submits form again
        chosennsorting = request.form.get("chosensorting")
        return render_template("history.html", total=totalexp, historylist=historylist, sorting_order=sorting_order)

    else: #if request.method == "GET":
        # List is sorted based on "date: old to new" by default (i.e if user uses GET so without selecting any sorting method)
        # Displays history in same way as "POST"
        historylist = db.execute(
        "SELECT * FROM spendings WHERE user_id = :current_id ORDER BY date", current_id=session["user_id"])
        totalo = db.execute(
        "SELECT details, SUM(amount) AS total FROM spendings WHERE user_id = :current_id", current_id=session["user_id"])
        if not totalo[0]["total"]:
            totalexp = 0
        else:
            totalexp = totalo[0]["total"]
        return render_template("history.html", total=totalexp, historylist = historylist, sorting_order="Date: old to recent")

@app.route("/stats")
@login_required
def stats():
    """Lets users view statistics related to their expenditures and budget"""
    # Create two lists that will constitude the data for a pie chart
    # The first list is made of the total number of dollars the user spent on each category
    # The second list is made of the names of the categories the user already spent money on
    listsums, listnames= [], []
    sums = db.execute(
            "SELECT category, SUM(amount) AS amount_categ FROM spendings WHERE user_id = :current_id GROUP BY category ORDER BY category", current_id=session["user_id"])
    for sum in sums:
        listsums.append(sum["amount_categ"])
        listnames.append(sum["category"])

    # Calculate percentage of budget used every month for the past 3 months
    # Retrieve user's monthly budget (info provided when signing up)
    rows = db.execute("SELECT * FROM users WHERE id = :current_id", current_id=session["user_id"])
    budgetnow = rows[0]["budget"]
    # Calculate percentage of monthly budget used on 1st month
    # by calculating total number of dollars user spent during that month, and dividing by budget then multiplying by 100
    budgetoc = db.execute(
        "SELECT details, SUM(amount) AS total FROM spendings WHERE user_id = :current_id AND date BETWEEN '2017-10-01' AND '2017-10-31'", current_id=session["user_id"])
    if not budgetoc[0]["total"]:
        totaloct=0
    else:
        totaloct=round((budgetoc[0]["total"]/budgetnow)*100, 2)
    # Do the same thing for the following two months
    budgetno = db.execute(
        "SELECT details, SUM(amount) AS total FROM spendings WHERE user_id = :current_id AND date BETWEEN '2017-11-01' AND '2017-11-31'", current_id=session["user_id"])
    if not budgetno[0]["total"]:
        totalnov=0
    else:
        totalnov=round((budgetno[0]["total"]/budgetnow)*100, 2)
    budgetde = db.execute(
        "SELECT details, SUM(amount) AS total FROM spendings WHERE user_id = :current_id AND date BETWEEN '2017-12-01' AND '2017-12-31'", current_id=session["user_id"])
    if not budgetno[0]["total"]:
        totaldec=0
    else:
        totaldec=round((budgetde[0]["total"]/budgetnow)*100, 2)
    # Passing all info above to template so that can be used by javascript to generate charts
    return render_template("stats.html", listsums=listsums, listnames=listnames, length=len(listsums), totaloct=totaloct, totalnov=totalnov, totaldec=totaldec)

@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    """Let user change their budget, email, and password information"""
    if request.method == "POST":
        # All validation of input is done through javascript on the template here as well
        if request.form['prefer'] == 'changebudget':
            # if successfully submits new budget request, update users table to contain that new number
            update = db.execute("UPDATE users SET budget = :newbudget WHERE id = :current_id",
                                current_id=session["user_id"], newbudget=request.form.get("newbud"))
            return redirect("/preferences")

        if request.form['prefer'] == 'changepass':
            # if successfully submits new password request, update users table to contain hash of new password
            rows = db.execute("SELECT * FROM users WHERE id = :id",
                                      id=session["user_id"])
            # Only allow action if inputted "old password" matches password in table
            if check_password_hash(rows[0]["hash"], request.form.get("oldpass")):
                update = db.execute("UPDATE users SET hash = :newhash WHERE id = :current_id",
                                    current_id=session["user_id"], newhash=generate_password_hash(request.form.get("newpass")))
                return redirect("/preferences")
            else:
                # Else display javascript alert on template thanks to 'wrongoldpass = 1'
                return render_template("preferences.html", wrongoldpass = 1)

        if request.form['prefer'] == 'changeemail':
            rows = db.execute("SELECT * FROM users WHERE id = :id",
                                      id=session["user_id"])
            rowss = db.execute("SELECT * FROM users WHERE email = :emaill",
                                  emaill=request.form.get("newemail"))
            # Check that new email not used yet (through len(rowss) == 0) and password entered is correct
            # and old email entered is correct
            if len(rowss) == 0:
                if check_password_hash(rows[0]["hash"], request.form.get("checkwithpass")) and rows[0]["email"] == request.form.get("oldemail"):
                    # if successfully submits new email request, update users table to contain new email
                    update = db.execute("UPDATE users SET email = :newemail WHERE id = :current_id",
                                        current_id=session["user_id"], newemail=request.form.get("newemail"))
                    return redirect("/preferences")
                else:
                    # if wrong password or wrong "old email", display javascript alert thanks to "wrongdata = 1"
                    return render_template("preferences.html", wrongdata = 1)
            else:
                # if inputted "new email" is already taken, display javascript alert thanks to "usedemail = 1"
                return render_template("preferences.html", usedemail = 1)

    else: #if request.method == "GET":
        # Retrieve user's current monthly budget to display it on web page
        rows = db.execute("SELECT * FROM users WHERE id = :current_id", current_id=session["user_id"])
        currbudget = rows[0]["budget"]
        return render_template("preferences.html", budget = currbudget)

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
