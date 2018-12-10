import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import urllib.parse
import classifier
from classifier import runFullScan, trainFullScan
import numpy as np
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import pickle

from functools import wraps

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///AIMES.db")

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

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/homepage")
@login_required
def homepage():
    curName = db.execute('SELECT firstName FROM users WHERE user_id=:user_id', user_id=session['user_id'])
    name = []
    name.append(curName[0]['firstName'])
    users = name[0].strip("'")
    return render_template('homepage.html', users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return ("must provide email")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return ("invalid email and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        users = db.execute('SELECT firstName from users WHERE user_id=:user_id', user_id=session['user_id'])
        # save,name = 0, []

        #for char in range(len(user)):
        #    if char == "'": save = 1
        #    if save == 1: name.append[user[char]]
        #users = content[3]

        # Redirect user to home page
        session["user_id"] = rows[0]["user_id"]
        curName = db.execute('SELECT firstName FROM users WHERE user_id=:user_id', user_id=session['user_id'])
        name = []
        name.append(curName[0]['firstName'])
        users = name[0].strip("'")
        return render_template("homepage.html", users=users)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/help")
@login_required
def helper():
    return render_template("help.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login formA
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # ensure first name isnt blank
        if not request.form.get('firstName'):
            return ('must provide first name')
        # ensure last name isnt blank
        elif not request.form.get('lastName'):
            return ('must provide last name')
        # ensure password isnt blank
        elif not request.form.get('password'):
            return ('must provide password')
        elif not request.form.get('email'):
            return ('must provide email')
        # check password
        elif request.form.get('password') != request.form.get('confirm'):
            return ('password is wrong')
        # insert user into database
        insert = db.execute('INSERT INTO users (lastName, firstName, email, hash, sex) VALUES(:lastName, :firstName, :email, :hash, :sex)',
                            firstName=request.form.get('firstName'), lastName=request.form.get('lastName'), email=request.form.get('email'), hash=generate_password_hash(request.form.get("password")), sex=request.form.get('sex'))
        # if not username has to be taken
        if not insert:
            return ('Error')
        return render_template('login.html')
    else:
        return render_template('register.html')

def errorhandler(e):
    """Handle error"""
    return (e.name, e.code)

@app.route("/quickscan", methods=["GET", "POST"])
@login_required
def quickscanner():
    if request.method == 'POST':
        if not request.form.get('heartRate') or not request.form.get('bloodPressureS') or not request.form.get('bloodPressureD') or not request.form.get('respiratoryRate') or not request.form.get('bodyTemp'):
            return ('Please fill out your Basic Info')
        if not request.form.get('sleep') or not request.form.get('aerobicActivity') or not request.form.get('drinks'):
            return ('Please fill out your Lifestyle')
        if not request.form.get('bloodGlucose') or not request.form.get('bloodOxidation') or not request.form.get('bloodAcidity'):
            return ('Please fill out your Minimal Blood Work')
        if not request.form.get('urineGlucose') or not request.form.get('urineAcidity'):
            return ('Please fill out your Minimal Urine Work')
        quick = db.execute('INSERT INTO quickscan (user_id, heartRate, bloodPressureS, bloodPressureD, respiratoryRate, bodyTemp, sleep, aerobicActivity, drinks, bloodGlucose, bloodOxidation, bloodAcidity, urineGlucose, urineAcidity) VALUES(:user_id, :heartRate, :bloodPressureS, :bloodPressureD, :respiratoryRate, :bodyTemp, :sleep, :aerobicActivity, :drinks, :bloodGlucose, :bloodOxidation, :bloodAcidity, :urineGlucose, :urineAcidity)',
                            user_id = session['user_id'], heartRate=request.form.get('heartRate'), bloodPressureS=request.form.get('bloodPressureS'), bloodPressureD=request.form.get('bloodPressureD'), respiratoryRate=request.form.get('respiratoryRate'), bodyTemp=request.form.get('bodyTemp'), sleep=request.form.get('sleep'), aerobicActivity=request.form.get('aerobicActivity'), drinks=request.form.get('drinks'), bloodGlucose=request.form.get('bloodGlucose'), bloodOxidation=request.form.get('bloodOxidation'), bloodAcidity=request.form.get('bloodAcidity'), urineGlucose=request.form.get('urineGlucose'), urineAcidity=request.form.get('urineAcidity'))
    else:
        return render_template('quickscan.html')
    userData = []
    curHr = db.execute('SELECT heartRate FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curHr[0]['heartRate'])
    curBps = db.execute('SELECT bloodPressureS FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBps[0]['bloodPressureS'])
    curBpd = db.execute('SELECT bloodPressureD FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBpd[0]['bloodPressureD'])
    curRr = db.execute('SELECT respiratoryRate FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curRr[0]['respiratoryRate'])
    curBt = db.execute('SELECT bodyTemp FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBt[0]['bodyTemp'])
    curs = db.execute('SELECT sleep FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curs[0]['sleep'])
    curAa = db.execute('SELECT aerobicActivity FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curAa[0]['aerobicActivity'])
    curd = db.execute('SELECT drinks FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curd[0]['drinks'])
    curBg = db.execute('SELECT bloodGlucose FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBg[0]['bloodGlucose'])
    curBo = db.execute('SELECT bloodOxidation FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBo[0]['bloodOxidation'])
    curBa = db.execute('SELECT bloodAcidity FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBa[0]['bloodAcidity'])
    curUg = db.execute('SELECT urineGlucose FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curUg[0]['urineGlucose'])
    curUa = db.execute('SELECT urineAcidity FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curUa[0]['urineAcidity'])
    loaded_model = pickle.load(open("quickModel.sav", "rb"))
    result = loaded_model.predict(np.expand_dims(userData, axis=1).T)
    result = result[0]
    curName = db.execute('SELECT firstName FROM users WHERE user_id=:user_id', user_id=session['user_id'])
    name = []
    name.append(curName[0]['firstName'])
    users = name[0].strip("'")
    #high, low = [], []
    #for col in range(len(upperRanges)):
        #if userData[col] < lowerRanges[col]:
            #low.append(problem[col])
        #elif userData[col] > upperRanges[col]:
            #high.append(problem[col])
    #print(high)
    #print(low)
    quickscan = db.execute('SELECT heartRate, bloodPressureS, bloodPressureD, respiratoryRate, bodyTemp, sleep, aerobicActivity, drinks, bloodGlucose, bloodOxidation, bloodAcidity, urineGlucose, urineAcidity FROM quickscan WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1',
                             user_id = session['user_id'])
    # db.execute('UPDATE clinicals SET classification= :result WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'], result = result)
    result = int(result)
    if result == 0:
        result = 'sick'
    elif result == 1:
        result = 'healthy'
    return render_template("result.html", users=users, result=result)

@app.route("/fullscan", methods=["GET", "POST"])
@login_required
def fullscanner():
    if request.method == 'POST':
        if not request.form.get('age') or not request.form.get('bp'):
            return ('please enter your age')
        if not request.form.get('bp'):
            return ('please enter your bp')
        if not request.form.get('rbc'):
            return ('please enter your rbc')
        if not request.form.get('pc'):
            return ('please enter your pc')
        if not request.form.get('pcc'):
            return ('please enter your pcc')
        if not request.form.get('ba'):
            return ('please enter your ba')
        if not request.form.get('bgr'):
            return ('please enter your bgr')
        insert = db.execute('INSERT INTO clinicals (user_id, age, bp, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wbcc, rbcc, htn, dm, cad, appet, pe, ane) Values(:user_id, :age, :bp, :rbc, :pc, :pcc, :ba, :bgr, :bu, :sc, :sod, :pot, :hemo, :pcv, :wbcc, :rbcc, :htn, :dm, :cad, :appet, :pe, :ane)',
                                user_id = session['user_id'], age=request.form.get('age'), bp=request.form.get('bp'), rbc=request.form.get('rbc'), pc=request.form.get('pc'), pcc=request.form.get('pcc'), ba=request.form.get('ba'), bgr=request.form.get('bgr'), bu=request.form.get('bu'), sc=request.form.get('sc'), sod=request.form.get('sod'), pot=request.form.get('pot'), hemo=request.form.get('hemo'), pcv=request.form.get('pcv'), wbcc=request.form.get('wbcc'), rbcc=request.form.get('rbcc'), htn=request.form.get('htn'), dm=request.form.get('dm'), cad=request.form.get('cad'),appet=request.form.get('appet'), pe=request.form.get('pe'), ane=request.form.get('ane'))
    else:
        return render_template('fullscan.html')
    userData = []
    curAge = db.execute('SELECT age FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curAge[0]['age'])
    curBp = db.execute('SELECT bp FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBp[0]['bp'])
    curRbc = db.execute('SELECT rbc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curRbc[0]['rbc'])
    curPc = db.execute('SELECT pc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curPc[0]['pc'])
    curPcc = db.execute('SELECT pcc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curPcc[0]['pcc'])
    curBa = db.execute('SELECT ba FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBa[0]['ba'])
    curBgr = db.execute('SELECT bgr FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBgr[0]['bgr'])
    curBu = db.execute('SELECT bu FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curBu[0]['bu'])
    curSc = db.execute('SELECT sc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curSc[0]['sc'])
    curSod = db.execute('SELECT sod FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curSod[0]['sod'])
    curPot = db.execute('SELECT pot FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curPot[0]['pot'])
    curHemo = db.execute('SELECT hemo FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curHemo[0]['hemo'])
    curPcv = db.execute('SELECT pcv FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curPcv[0]['pcv'])
    curWbcc = db.execute('SELECT wbcc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curWbcc[0]['wbcc'])
    curRbcc = db.execute('SELECT rbcc FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curRbcc[0]['rbcc'])
    curHtn = db.execute('SELECT htn FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curHtn[0]['htn'])
    curDm = db.execute('SELECT dm FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curDm[0]['dm'])
    curCad = db.execute('SELECT cad FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curCad[0]['cad'])
    curAppet = db.execute('SELECT appet FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curAppet[0]['appet'])
    curPe = db.execute('SELECT pe FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curPe[0]['pe'])
    curAne = db.execute('SELECT ane FROM clinicals WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'])
    userData.append(curAne[0]['ane'])
    loaded_model = pickle.load(open("classifier.sav", "rb"))
    result = loaded_model.predict(np.expand_dims(userData, axis=1).T)
    result = result[0]
    curName = db.execute('SELECT firstName FROM users WHERE user_id=:user_id', user_id=session['user_id'])
    name = []
    name.append(curName[0]['firstName'])
    users = name[0].strip("'")
    # db.execute('UPDATE clinicals SET classification= :result WHERE user_id=:user_id ORDER BY time_created DESC LIMIT 1', user_id = session['user_id'], result = result)
    if result == 1:
        return render_template("resultHealthy.html", users = users)
    if result == 0:
        return render_template("resultSick.html", users = users)

#@app.route("/result", methods=["GET", "POST"])
#def check():
    #"""integrate backend"""
    #curData = db.execute('SELECT age, bp, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wbcc, rbcc, htn, dm, cad, appet, pe, ane FROM clinicals WHERE user_id=:user_id ORDER BY time_created ASC', user_id= session['user_id'])
    #print(curData)
    #if classifier.runcheck(z, protoData)  == 1:
        #return render_template('result.html', result = 'You have Chronic Kidney Disease, seek out professional help')
        #db.execute('INSERT INTO clinicals (class) Values(:class) WHERE user_id=:user_id ORDER BY time_created ASC', user_id=session['user_id'])
    #elif classifier.runcheck(z, protoData) == 0:
        #return render_template('result.html', result = 'You are healthy')
    #else:
        #return render_templace('fullscan.html')

# listen for errors
#for code in default_exceptions:
 #   app.errorhandler(code)(errorhandler)