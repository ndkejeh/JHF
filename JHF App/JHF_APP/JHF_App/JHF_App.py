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

    def __init__(self, fname, lname, dob, retirement_age):
        self.fname = fname
        self.lname = lname
        self.dob = datetime.strptime(dob, "%Y-%m-%d").date()
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

@app.route("/searchprospect")
def searchprospect():
    return render_template("change-view.html")

@app.route("/jhf/api/v1.0/prospects", methods=["GET", "POST"]) #this will be the api for add user
def new_prospect():
    if not request.is_json:
        abort(400) #data sent wasn't JSON so about with an error else process
    #else continue
    if request.method == 'POST':
        #use validation in the form - therefore will have to change to a form
        new_entry = prospects(request.json["FirstName"], request.json["Surname"], request.json["Dob"], request.json["Retirement"])
        db.session.add(new_entry)
        db.session.commit()
        entered = {
            "FirstName": new_entry.fname,
            "Surname": new_entry.lname,
            "DOB": new_entry.dob,
            "Retirement": new_entry.retirement_age,
        }
        return jsonify(entered),201 #201 is HTTP code for created
    elif request.method == "GET":
        target = prospects.query.filter_by(fname=request.json["fname"],
         lname=request.json["lname"], dob=request.json["dob"]).first()
        if not target is none: #then we have found a match
            found = {
                "id": target.id,
                "fname": target.fname,
                "lname": target.lname,
                "dob": target.dob,
                "retirement": target.retirement_age,
            }
            return jsonify(found), 200 #send back the result found inc. ID
        else:
            return 404 #i.e. not found

@app.route("/jhf/api/v1.0/prospects/find", methods=["POST"])
def find_prospect(): #this api finds a prospect from the info posted and returns
    if request.method == "POST":
        target = prospects.query.filter_by(fname=request.json["fname"], dob=datetime.strptime(request.json["dob"], "%Y-%m-%d").date()).first()
        if not target is None: #then we have found a match
            # truncdob = datetime.strptime(target.dob, "%Y-%m-%d").date()
            found = {
                "id": target.id,
                "fname": target.fname,
                "lname": target.lname,
                "dob": target.dob.strftime("%d/%m/%Y"),
                "retirement": target.retirement_age,
            }
            return jsonify(found), 200 #send back the result found inc. ID
        else:
            return 404 #i.e. not found


@app.route("/jhf/api/v1.0/prospects/<int:prosp_id>", methods=["PUT", "DELETE"]) #The api for updating a prospect
def update_prospect(prosp_id):
    if prosp_id is not None:
        target = prospects.query.get(prosp_id)
        if request.method =="PUT":
            #Need to find code that checks there's something in Kwarg before equating!!
            target.fname = request.json["fname"]
            target.lname = request.json["lname"]
            db.session.add(target)
        elif request.method =="DELETE":
            db.session.delete(target)
        db.session.commit()

    updated_prosp = {
        "fname": target.fname,
        "lname": target.lname,
        "dob": target.dob,
        "Retirement": target.retirement_age,
        "status": "201", #success created HTML status code
    }
    return jsonify(updated_prosp)



if __name__ == "__main__":
    app.run(debug=True)