from flask import Flask, render_template, request, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.parser import parser

app = Flask(__name__)
#db = sqlite3.connect('clients.db') #creates a new db if it doesn't exist
#db.close()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:jkl64fds@localhost:3306/jhf_db"
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

@app.route("/")
def index():
    return  render_template("index.html")

@app.route("/adduser")
def adduser():
    return render_template("newprospect.html")

@app.route("/jhf/api/v1.0/prospects", methods=["GET", "POST"]) #this will be the api for add user
def submitted():
    if request.method == 'POST':
        if not request.is_json:
            abort(400) #data sent wasn't JSON so about with an error else process

        new_entry = prospects(request.json["FirstName"], request.json["Surname"], request.json["Retirement"])
        db.session.add(new_entry)
        db.session.commit()
        entered = {
            "FirstName": new_entry.fname,
            "Surname": new_entry.lname,
            "DOB": new_entry.dob,
            "Retirement": new_entry.retirement_age,
        }
        return jsonify(entered),201 #201 is HTTP code for created
    else:
        return "It's likely a GET submission!"
    #You then need the request method to access the data
    #request.form['firstname']

if __name__ == "__main__":
    app.run(debug=True)
