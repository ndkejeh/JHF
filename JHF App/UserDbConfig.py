from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.parser import parser

app = Flask(__name__)
#db = sqlite3.connect('clients.db') #creates a new db if it doesn't exist
#db.close()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:jkl64fds@localhost:3300/jhf_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db  = SQLAlchemy(app)

class prospects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(45))
    lname = db.Column(db.String(45))
    dob = db.Column(db.Date)
    retirement_age = db.Column(db.Integer)
    referrer_id = db.Column(db.Integer, db.ForeignKey('referrers.id'))

    def __init__(self, fname, lname,retirement_age):
        self.fname = fname
        self.lname = lname
    #    self.dob = datetime.strptime(dob, "%Y-%m-%d")
        self.retirement_age = retirement_age

class referrers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(45))
    industry = db.Column(db.String(100))
    prospects = db.relationship('prospects', backref='referrers', lazy='dynamic')
