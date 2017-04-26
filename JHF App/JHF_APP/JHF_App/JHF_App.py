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

    def __init__(self, **kwargs): #the initial method on create a prospect instance
        for newData in kwargs:
            if kwargs[newData] is not "":
                if newData == "dob": #then format date for input
                    kwargs[newData] = datetime.strptime(kwargs[newData], "%d/%m/%Y").date()
                setattr(self, newData, kwargs[newData])

class referrers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(45))
    industry = db.Column(db.String(100))
    prospects = db.relationship('prospects', backref='referrers', lazy='dynamic')

def dateFormat(badDate):
    #takes a null or a date passed in the %d/%m/%Y format
    if badDate is None: #then send back without format
        return None
    else:
        goodDate = badDate.strftime("%d/%m/%Y")
        return(goodDate)

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
        #new_entry = prospects(request.json["fname"], request.json["lname"], request.json["dob"], request.json["retirement_age"])
        new_entry = prospects(**request.json)
        db.session.add(new_entry)
        db.session.commit()
        entered = {
            "fname": new_entry.fname,
            "lname": new_entry.lname,
            "dob": new_entry.dob,
            "retirement_age": new_entry.retirement_age,
            "status": "201", #201 is HTTP code for created
        }
        return jsonify(entered),201
    # elif request.method == "GET": #delete this, don't let a search happen over GET
    #     target = prospects.query.filter_by(fname=request.json["fname"],
    #      lname=request.json["lname"], dob=request.json["dob"]).first()
    #     if not target is None: #then we have found a match
    #         found = {
    #             "id": target.id,
    #             "fname": target.fname,
    #             "lname": target.lname,
    #             "dob": target.dob,
    #             "retirement": target.retirement_age,
    #         }
    #         return jsonify(found), 200 #send back the result found inc. ID
    #     else:
    #         return 404 #i.e. not found

@app.route("/jhf/api/v1.0/prospects/find", methods=["POST"])
def find_prospect(): #this api finds a prospect from the info posted and returns
    if request.method == "POST":
        found = {} #empty dictionary for response
        if "dob" in request.json and request.json["dob"] is not "": #then format it ahead of time
            request.json["dob"] = datetime.strptime(request.json["dob"], "%d/%m/%Y").date()
        #Now make an array where we keep only the sent search strings
        searchFields = {} #empty dictionary
        for searchKeys in request.json: #make a dict of actual included search strings
            if request.json[searchKeys] is not "":
                searchFields[searchKeys] = request.json[searchKeys]
        target = prospects.query.filter_by(**searchFields).first()
        if target is not None: #then we have found a match
            # truncdob = datetime.strptime(target.dob, "%Y-%m-%d").date()
            # for fieldKeys in target:
            #     found[fieldKeys] = getattr(target, fieldKeys)
            statusCode = "200"
            # searchStatus = "Found"
            found = {
                "id": target.id,
                "fname": target.fname,
                "lname": target.lname,
                "dob": dateFormat(getattr(target,"dob")),
                "retirement_age": target.retirement_age,
                "status": "200",
                "response": "Found",
            }
            #return jsonify(found), 200 #send back the result found inc. ID
        else:
            statusCode = "404"
            # searchStatus = "Not Found"
            found = {
                "id": "",
                "fname": "",
                "lname": "",
                "dob": "",
                "retirement_age": "",
                "status": "404",
                "response": "Not Found",
            }
        # found["status"] = status
        # found["response"] = searchStatus
        return jsonify(found), statusCode
        #return ("Prospect Not Found"), 404 #i.e. not found


@app.route("/jhf/api/v1.0/prospects/<int:prosp_id>", methods=["PUT", "DELETE"]) #The api for updating a prospect
def update_prospect(prosp_id):
    if prosp_id is not None:
        target = prospects.query.get(prosp_id)
        if request.method == "DELETE": #delete the prospect and leave
            db.session.delete(target)
            returnCode = "204" #i.e. success delete (no content)
            action = "Deleted"
        elif request.method == "PUT":
            #Need to find code that checks there's something in Kwarg before equating!!
            for updateKey in request.json:
                if updateKey == "dob": #then we have to condition the entry
                    request.json[updateKey] = datetime.strptime(request.json[updateKey], "%d/%m/%Y").date()
                setattr(target, updateKey, request.json[updateKey])
            db.session.add(target)
            returnCode = "201" #success created HTML status code
            action = "Updated"
        else:
            abort(400) #exit with bad code as not PUT or DELETE
        #Return preparation
        updated_prosp = {
            "fname": target.fname,
            "lname": target.lname,
            "dob": dateFormat(getattr(target,"dob")),
            "retirement_age": target.retirement_age,
            "status": returnCode,
            "action": action,
        }
        db.session.commit()
        return jsonify(updated_prosp)




if __name__ == "__main__":
    app.run(debug=True)
