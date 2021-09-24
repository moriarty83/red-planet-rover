import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json
import math
import random
import sys

from helpers import apology, login_required, lookup, manifest, lookupCamera, add

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

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mars.db")

# Make sure API key is set API Key - Run this in terminal: export API_KEY=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods = ["GET", "POST"])
def index():
    """Show Rovers and Enter Sols"""

    if request.method == 'POST':
        sol = None
        rover = None

        if request.form["submit"] == "spirit":
            sol = request.form.get("solSpirit")
            rover = "spirit"
        if request.form['submit'] == 'opportunity':
            sol = request.form.get("solOpportunity")
            rover = "opportunity"
        if request.form['submit'] == 'curiosity':
            sol = request.form.get("solCuriosity")
            rover = "curiosity"

        return render_template("display.html", rover=rover, sol=sol)
    else:

        userid = session.get("user_id")
        print('Hello world!', file=sys.stderr)

        spiritSols = manifest("spirit")
        curiositySols = manifest("curiosity")
        opportunitySols = manifest("opportunity")

        return render_template("index.html" , spiritSols = spiritSols, curiositySols = curiositySols, opportunitySols=opportunitySols)


@app.route("/images", methods=["GET", "POST"])
def images():
    """Display Images"""
    if request.method == 'POST':
        rover = None
        input = None
        action = None



        print("Running Post")
        action = request.form.get("action")
        input = request.form.get("input")
        rover = request.form.get("submit")
        print (action)
        print (input)
        print (rover)


        images = lookup(rover, input, action)[0]
        cameras = lookup(rover, input, action)[1]


        if len(images) < 2:
            flash("No images available")
            spiritManifest = manifest("spirit")
            curiosityManifest = manifest("curiosity")
            opportunityManifest = manifest("opportunity")
            return render_template("images.html", spiritManifest = spiritManifest, curiosityManifest = curiosityManifest, opportunityManifest = opportunityManifest)


        for camera in cameras:
            print(camera[0])
            print(camera[1])

        return render_template("display.html", images=images, rover=rover, cameras=cameras, action=action, input=input)

    else:
        userid = session.get("user_id")

        suggestions = ["Have you tried looking up the Sol of your lucky number?", "Did you know Curiosity spotted a comet on Sol 783?", "Spirit took a photo of the memorial plaque to the crew of the Columbia on Spirit, Sol 2.", "Have you tried looking up your sweetheart’s birthday?", "Have you tried looking up your birthday?", "Have you tried up your child’s birthday?", "Have you tried seeing what rovers were doing on your anniversary?", "Nothing says ‘I Love You’ like a picture from Mars on Valentine’s Day Rover.", "On Sol 16, Spirit took a great shot of the Columbia Memorial Station.", "On Sol 4332 Opportunity spotted a wicked dust devil.", "On Sol 335 Opportunity was reunited with its old friend Heat Shield.", "Ever wonder if any rovers got a visit from Santa on Christmas?", "Don’t forget to check out the Martian dust storm Curiosity captured on June 7 – 10, 2018.", "Ever wonder how rovers celebrate the Earth New Year?", "Spirit captured some amazing rock formations on Sol 774.", "Spirit snapped an excellent Martian sunset on Sol 489.", "On Sol 543 Spirit captured a Martian dust devil.", "See how Opportunity celebrated Rosh Hashana on September 22, 2007.", "See how Curiosity celebrated the end of Ramadan on July 17, 2015.", "What do you think Spirit sent home on Mothers’ Day, May 11, 2008."]
        suggestion = random.choice(suggestions)
        print("suggestion is" + suggestion)

        spiritManifest = manifest("spirit")
        curiosityManifest = manifest("curiosity")
        opportunityManifest = manifest("opportunity")
        return render_template("images.html", spiritManifest = spiritManifest, curiosityManifest = curiosityManifest, opportunityManifest = opportunityManifest, suggestion=suggestion)

@app.route("/display", methods=["GET", "POST"])
def display():
    """Get stock quote."""
    if request.method == 'POST':

        rover = request.form.get("rover")
        action = request.form.get("action")
        input = request.form.get("input")
        earthDate = request.form.get("earthdate")
        images = session["sessionImages"]
        if request.form.get("action") == "add":
            if session.get("user_id") == None:
                return render_template("login.html")

            else:
                print("action is Add")
                if add() is 0:
                    flash ("Image Already in Gallery")
                    cameras = session["camImages"]
                    return render_template("display.html", images=images, rover=rover, cameras=cameras, action=action, input=input)
                else:
                    flash ("Image Added to Gallery")
                    cameras = session["camImages"]
                    return render_template("display.html", images=images, rover=rover, cameras=cameras, action=action, input=input)

        else:
            print("viewing all")
            action = request.form.get("action")
            input = request.form.get("input")
            rover = request.form.get("rover")
            camera = request.form.get("cameraCode")
            camImages = session["camImages"]
            for cam in camImages:
                if cam[1]==camera:
                    index = camImages.index(cam)
            images = camImages[index]
            session["cameraImages"] = images
            session["camera"] = camera
            session["rover"] = rover
            print(len(images))
            return render_template("viewall.html", images=images, camera=camera, rover=rover)

    else:
        return render_template("display.html")

@app.route("/viewall", methods = ["POST"])
def viewall():
    """Display All"""
    camImages = session["camImages"]
    images = session["cameraImages"]
    camera = session["camera"]
    rover = session["rover"]

    if request.method == "POST":
        if session.get("user_id") == None:
            return render_template("login.html")

        else:
            print("Running Viewall Post")


            if add() is 0:
                flash ("Image Already in Gallery")
                return render_template("viewall.html", images=images, camera=camera, rover=rover)
            else:
                flash ("Image Added to Gallery")

                return render_template("viewall.html", images=images, camera=camera, rover=rover)

    else:
        camImages=session["camImages"]
        return render_template("viewall.html", images=camImages)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_idif
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash ("Must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash ("Must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash ("Invalid Username or Password")
            return render_template("login.html")

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
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmPassword"):
            return apology("must confirm password", 403)

        elif request.form.get("confirmPassword") != request.form.get("password"):
            return apology("passwords do not match", 403)

        elif len(request.form.get("password")) < 6:
            return apology("Password must be at least six characters")

        nonAlphas = 0;

        for char in request.form.get("password"):
            if not char.isalpha():
                nonAlphas += 1;

        if nonAlphas < 2:
            return apology ("Password mus contain 2 non-letter characters")

        username = request.form.get("username")
        password = request.form.get("password")
        hash = generate_password_hash(password)
        cpword = request.form.get("confirmPassword")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) > 0:
            return apology("username already exists", 403)

        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",username=username, hash=hash)
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/registered", methods=["GET"])
def registered():
    return


@app.route("/gallery", methods=["GET", "POST"])
@login_required
def gallery():
    if request.method == "POST":

        userid = session.get("user_id")
        imageid = request.form.get("imageid")
        db.execute("DELETE FROM gallery WHERE userid = (:userid) AND imageid = (:imageid)", userid=userid, imageid=imageid)
        userGallery = db.execute("SELECT * FROM gallery WHERE userid is (:userid)", userid=userid)

        return render_template("gallery.html", gallery=userGallery)

    else:
        userid = session.get("user_id")
        userGallery = db.execute("SELECT * FROM gallery WHERE userid is (:userid)", userid=userid)

        return render_template("gallery.html", gallery=userGallery)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


@app.route("/learn", methods=["GET"])
def learn():
    return render_template("learn.html")

