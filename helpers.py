import os
import requests
import urllib.parse
import urllib.request
import ssl
import sys
import certifi
import json
from cs50 import SQL
from datetime import datetime

from flask import redirect, render_template, request, session
from functools import wraps
from pandas.io.json import json_normalize
import pandas as pd

db = SQL("sqlite:///mars.db")

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


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#Mission Manifest
#https://api.nasa.gov/mars-photos/api/v1/manifests/Curiosity/?api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq

def lookupCamera(rover, input, action, camera):
    print("Camera Lookup")
    print(rover)
    print(input)
    print(camera)
    if action == "Sol":
        with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol={input}&&camera={camera}&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq", context=ssl.create_default_context(cafile=certifi.where())) as response:
            data = response.read()
            images = json.loads(data)
            return images["photos"]

    else:
        with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?earth_date={input}&&camera={camera}&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq", context=ssl.create_default_context(cafile=certifi.where())) as response:
            data = response.read()
            images = json.loads(data)
        return images["photos"]

def manifest(rover):
    """Look rover mission manifest."""

    maxSol = None

    #https://api.nasa.gov/mars-photos/api/v1/manifests/Curiosity/?api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq
    # Contact API
    # {urllib.parse.quote_plus(symbol)}

    api_key = "S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq"
    with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/manifests/{rover}/?api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq", context=ssl.create_default_context(cafile=certifi.where())) as response:
        data = response.read()

    manifest = json.loads(data)
    print('Hello Manifest!', file=sys.stderr)

    return manifest["photo_manifest"]

def add():
    print("Running Add")
    dateTime = datetime.now()
    userid = session.get("user_id")
    userRecord = db.execute("SELECT * FROM users WHERE id = (:userid)", userid=userid)
    user = userRecord[0]["username"]
    image = request.form["submit"]

    imageid = request.form.get("imageid")
    rover = request.form.get("rover")
    print ("rover is " + rover)
    sol = request.form.get("sol")
    earthdate = request.form.get("earthdate")
    camera = request.form.get("camera")
    img_src = request.form.get("img_src")
    print(rover)
    submittedFrom = request.form.get("submittedFrom")


    if db.execute("SELECT imageid FROM gallery WHERE imageid = (:imageid)", imageid=imageid):
        return 0

    else:
        db.execute("INSERT INTO gallery (user, userid, dateTime, rover, sol, camera, earthdate, imageid, img_src) VALUES(:user, :userid, :dateTime, :rover, :sol, :camera, :earthdate, :imageid, :img_src)", user=user, userid=userid, dateTime=dateTime, rover=rover, sol=sol, camera=camera, earthdate=earthdate, imageid=imageid, img_src=img_src)
        return 1

def lookup(rover, input, action):

    images = None
    cameraName = None
    api_key = "S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq"

    print("rover is " + rover)
    print("input is " + str(input))
    print("action is " + action)

    if action == "Sol":
        print("https://api.nasa.gov/mars-photos/api/v1/rovers/" + rover + "/photos?sol=" + input + "&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq")
        with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol={input}&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq", context=ssl.create_default_context(cafile=certifi.where())) as response:
            data = response.read()
            file = json.loads(data)
            print("Running Post Display Sol")

            session["sessionImages"] = file["photos"]
            images = session["sessionImages"]
            print(images)

    if action == "earthDate":
        print("Running Display Earth Date")
        print("https://api.nasa.gov/mars-photos/api/v1/rovers/" + rover + "/photos?earth_date=" + input + "&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq")
        with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?earth_date={input}&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq", context=ssl.create_default_context(cafile=certifi.where())) as response:
            data = response.read()
            file = json.loads(data)

            session["sessionImages"] = file["photos"]
            images = session["sessionImages"]

    if rover == "curiosity":
        cameraCodes =["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM"]
        cameras = [["Front Hazard Avoidance Camera"], ["Rear Hazard Avoidance Camera"], ["Mast Camera"], ["Chemistry and Camera Complex"], ["Mars Hand Lens Imager"], ["Mars Descent Imager"], ["Navigation Camera"]]
    else:
        cameraCodes =["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
        cameras = [["Front Hazard Avoidance Camera"], ["Rear Hazard Avoidance Camera"], ["Navigation Camera"], ["Panoramic Camera"], ["Miniature Thermal Emission Spectrometer (Mini-TES)"]]

    for i in range(0, len(cameras)):
        cameras[i].append(cameraCodes[i])

    for row in images:
        for camera in cameras:

            if str(row["camera"]["full_name"]) in str(camera):
                #print("match!")
                cameras[cameras.index(camera)].append(row)

    session["camImages"] = cameras

    return images, cameras,

def displayImagesEarthDate(rover, date):
    images = None
    cameraName = None
    # Contact API
    # {urllib.parse.quote_plus(symbol)}
    api_key = "S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq"

    with urllib.request.urlopen(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?earth_date={date}&api_key=S6RM23qrCp3bkS3MpJ3NqqOgUs8eUeSZ14sCKcEq") as response:
        data = response.read()
        file = json.loads(data)

        print("Running Display Earht Date")

        session["sessionImages"] = file["photos"]
        images = session["sessionImages"]

        print(images)

    if rover is "curiosity":
        cameraCodes =["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM"]
        cameras = [["Front Hazard Avoidance Camera"], ["Rear Hazard Avoidance Camera"], ["Mast Camera"], ["Chemistry & Camera Complex"], ["Mars Hand Lens Imager"], ["Mars Descent Imager"], ["Navigation Camera"]]
    else:
        cameraCodes =["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
        cameras = [["Front Hazard Avoidance Camera"], ["Rear Hazard Avoidance Camera"], ["Navigation Camera"], ["Panoramic Camera"], ["Miniature Thermal Emission Spectrometer (Mini-TES)"]]

    for i in range(0, len(cameras)):
        cameras[i].append(cameraCodes[i])

    for row in images:
        for camera in cameras:

            if str(row["camera"]["full_name"]) in str(camera):
                #print("match!")
                cameras[cameras.index(camera)].append(row)

    index = None

    return images, cameras,