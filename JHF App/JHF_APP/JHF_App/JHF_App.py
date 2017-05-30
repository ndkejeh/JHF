from flask import Flask, render_template, request, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.parser import parser

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:jkl64fds@localhost:3306/jhf_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db  = SQLAlchemy(app)

class contributions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(15,2))
    ctype = db.Column(db.String(11), nullable=False)
    cto = db.Column(db.String(10), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is not "":
                setattr(self, newData, kwargs[newData])

class notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    ntype = db.Column(db.String(7))
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is "" and newData == "ntype":
                setattr(self,newData, "Private")
            else:
                setattr(self, newData, kwargs[newData])

class expenditures(db.Model): #has a one-to-one relationship with prospects
    id = db.Column(db.Integer, primary_key=True)
    currentspend = db.Column(db.Numeric(15,2), nullable=False)
    goldenspend = db.Column(db.Numeric(15,2), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is not "":
                setattr(self, newData, kwargs[newData])

class assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.Numeric(15,2))
    atype = db.Column(db.String(10), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is "" and newData == "atype":
                setattr(self,newData, "Pension")
            else:
                setattr(self, newData, kwargs[newData])

class interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interest = db.Column(db.String(18))
    itype = db.Column(db.String(8), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is "" and newData == "itype":
                setattr(self,newData, "Service")
            else:
                setattr(self, newData, kwargs[newData])

class prospects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(45))
    lname = db.Column(db.String(45))
    dob = db.Column(db.Date)
    retirement_age = db.Column(db.Integer)
    #These are the parent relationships below
    referrer_id = db.Column(db.Integer, db.ForeignKey('referrers.id'))
    #These are the one-to-one relationships below
    expenditures = db.relationship('expenditures', backref='prospects',uselist=False)
    #These are the one-to-many relationships below
    constributions = db.relationship('contributions', backref='prospects', lazy='dynamic')
    notes = db.relationship('notes', backref='prospects', lazy='dynamic')
    assets = db.relationship('assets', backref='prospects', lazy='dynamic')
    interests = db.relationship('interests', backref='prospects', lazy='dynamic')

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

#//START OF CUSTOM FUNCTIONS
def dateFormat(badDate):
    #takes a null or a date passed in the %d/%m/%Y format
    if badDate is None: #then send back without format
        return None
    else:
        goodDate = badDate.strftime("%d/%m/%Y")
        return(goodDate)

def appendToList(**kwargs):
    kwargDict = {}
    for keys in  kwargs:
        kwargDict[keys] = kwargs[keys]
    return kwargDict

@app.route("/")
def index():
    return  render_template("index.html")

@app.route("/adduser")
def adduser():
    return render_template("newprospect.html")

@app.route("/searchprospect")
def searchprospect():
    return render_template("change-view.html")

@app.route("/goldennum")
def goldennumber():
    return render_template("goldennumber.html")

@app.route("/jhf/api/v1.0/prospects", methods=["POST"]) #this will be the api for add user
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

@app.route("/jhf/api/v1.0/prospects/find", methods=["POST"])
#THE API FOR RETURNINIG MULTIPLE RESULTS OF A QUERY - THE ONE BELOW CONSTRAINS RESULTS TO ONE!
def find_prospects(): #this api finds a prospect from the info posted and returns
    if request.method == "POST": #don't need this as there is a strict post method only in declaration
        #found = {} #empty dictionary for response
        if "dob" in request.json and request.json["dob"] is not "": #then format it ahead of time
            request.json["dob"] = datetime.strptime(request.json["dob"], "%d/%m/%Y").date()
        #Now make an array where we keep only the sent search strings
        searchFields = {} #empty dictionary
        for searchKeys in request.json: #make a dict of actual included search strings
            if request.json[searchKeys] is not "" and searchKeys != "find":
                searchFields[searchKeys] = request.json[searchKeys]
        target = prospects.query.filter_by(**searchFields).all()
        #check if target is a list of objects or just a single object (single result)
        if isinstance(target, list) and request.json["find"] != 1:
            #then there are multiple results andour default is for user to take all results unless indicate 1
            multResult = []
            for x in range(len(target)):
                singleTarget = target.pop(0) #take out head object in the list
                scalarFound = {
                    "id": singleTarget.id,
                    "fname": singleTarget.fname,
                    "lname": singleTarget.lname,
                    "dob": dateFormat(getattr(singleTarget,"dob")),
                    "retirement_age": singleTarget.retirement_age,
                }
                multResult.append(scalarFound)
            #And now make return string
            foundResponse = {
                "queryList": multResult,
                "length": x+1,
                "status": "200",
                "response": "Found",
            }
            return jsonify(foundResponse), 200
        elif target is not None: #then something has been found but only return first result
            targetScalar = prospects.query.filter_by(**searchFields).first()
            foundResponse = {
                "id": targetScalar.id,
                "fname": targetScalar.fname,
                "lname": targetScalar.lname,
                "dob": dateFormat(getattr(targetScalar,"dob")),
                "retirement_age": targetScalar.retirement_age,
                "status": "200",
                "response": "Found",
            }
            return jsonify(foundResponse), 200
        else:
            # searchStatus = "Not Found"
            foundResponse = {
                "id": None,
                "fname": None,
                "lname": None,
                "dob": None,
                "retirement_age": None,
                "status": "404",
                "response": "Not Found",
            }
            return jsonify(foundResponse), 404

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

@app.route("/jhf/api/v1.0/prospects/gndetails/<int:prosp_id>", methods=["POST", "PUT", "DELETE"]) #the api for updating/adding new prospects and deleting
def prospect_gndetails(prosp_id):
    if prosp_id is not None:
        owner = prospects.query.get(prosp_id) #put the right prospect into the owner object
        if owner == None: #then there is no prospect that exist with this ID so abort
            return("Prospect does not exist"), 400
        if request.method == "POST":
            #ObbjDict below stores class memory locations and info on required and constrained cols
            #if the column is a key in the tables key area then it has prescribed values (if a list), or is required if not
            objDict = {"expenditures": [{"classaddr": expenditures, "currentspend": "required", "goldenspend": "required"}],
                "assets": [{"classaddr": assets, "atype": ["Property", "Pension", "Investment", "Fixed"]}],
                "contributions": [{"classaddr": contributions, "ctype": ["Monthly", "Annual", "Lump Sum", "Final Salary"]}],
                "interests": [{"classaddr": interests, "itype": ["Services", "Purchases"]}],
                "notes": [{"classaddr": notes, "ntype": ["Private", "Public"]}]}
            responseDict = {}
            multiDictList = []
            for key in request.json:
                if isinstance(request.json[key], list): #then it's an array of objects with table values
                    #THIS IS WHERE WE SHOULD DO THE VALIDATION!!
                    for count, val in enumerate(request.json[key]): #I relaly only want the count but don't know how to do this withough getting both
                        for newCols in request.json[key][count]:
                            for specialCols in objDict[key][0]:
                                if newCols == specialCols: #then this is a protected column
                                    if isinstance(objDict[key][0][specialCols], list): #then there are prescribed values for col
                                        goodVal = 0
                                        for prescribedVals in objDict[key][0][specialCols]:
                                            if prescribedVals == request.json[key][count][newCols]: #Good, it has an allowed value
                                                goodVal = 1
                                        if goodVal == 0:
                                            return("Bad value in table %s number %s, column %s" %(key, (count+1), newCols)), 400
                                    else: #it's a required field and states that in its key-value pair
                                        if request.json[key][count][newCols] is None or request.json[key][count][newCols] is "": #then bad empty val
                                            return("%s column in %s table cannot be empty" %(newCols, key)), 400
                    #End of validation - anything that gets here has passed and new entry can begin
                    for z in range(len(request.json[key])):
                        if key == "expenditures" and owner.expenditures is not None: #for one-to-many integrity
                            return("This prospect already has expenditure data"), 400 #an expenditure entry already exists, need to update not add new!!
                        kwargList = request.json[key].pop(0)
                        multiDictList.append(appendToList(**kwargList))
                        kwargList["prospects"] = owner #this will handle the foreign key field linking to prospects
                        #APPEND TO AN EMPTY LIST HERE FOR THE OUTPUT
                        newRow = objDict[key][0]["classaddr"](**kwargList) #makes a new row/obj in table key
                        db.session.add(newRow)
                    responseDict[key] = multiDictList
                    multiDictList = []
            return jsonify(responseDict)
            db.session.commit() #now all will be committed if there's no error
            responseDict["status"] = "success"
            return jsonify(responseDict), 200
        #elif request.method == "PUT"
    else:
        abort(404)

#THE Gn Details SEARCH API
@app.route("/jhf/api/v1.0/prospects/gndetails/find/<int:prosp_id>", methods=["POST"]) #the api for updating/adding new prospects and deleting
def searchProspectGndetails(prosp_id):
    if prosp_id is not None:
        owner = prospects.query.get(prosp_id)
        if owner == None: #then prospect doesn't exist abort
            return jsonify("Prospect does not exist"), 400
        tableAddrs = {"assets": assets, "contributions": contributions, "notes": notes,
            "expenditures": expenditures, "interests": interests} #dict of tables and their class addresses
        if request.json["specificTables"] is not None: #then there is a request for only specific tables' data
            if isinstance(request.json["specificTables"], list): #then proper format
                #check table matches in sent specifics of what was sent
                returnedTables = list(filter(lambda x: x in tableAddrs, request.json["specificTables"]))
                if returnedTables == []:
                    return jsonify("please enter proper table names all in small caps"), 400
                else: #search and return results from tables in returnedTables
                    objList = list(map(lambda x: tableAddrs[x].query.filter_by(prospects = owner).all(), returnedTables))
                    return (str(objList))


    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
