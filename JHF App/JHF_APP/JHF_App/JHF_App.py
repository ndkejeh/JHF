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

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "amount": str(self.amount),
            "ctype": self.ctype,
            "cto": self.cto,
        }
        return objToDict

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
    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "note": self.note,
            "ntype": self.ntype,
        }
        return objToDict

class expenditures(db.Model): #has a one-to-one relationship with prospects
    id = db.Column(db.Integer, primary_key=True)
    currentspend = db.Column(db.Numeric(15,2), nullable=False)
    goldenspend = db.Column(db.Numeric(15,2), nullable=False)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'))

    def __init__(self, **kwargs):
        for newData in kwargs:
            if kwargs[newData] is not "":
                setattr(self, newData, kwargs[newData])

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "currentspend": str(self.currentspend),
            "goldenspend": str(self.goldenspend),
        }
        return objToDict

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

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "name": self.name,
            "value": str(self.value),
            "atype": self.atype,
        }
        return objToDict

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

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "interest": self.interest,
            "itype": self.itype,
        }
        return objToDict

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

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "fname": self.fname,
            "lname": self.lname,
            "dob": self.dob.strftime("%d/%m/%Y"), #formatted for output
            "retirement_age": self.retirement_age,
        }
        return objToDict

class referrers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(45))
    industry = db.Column(db.String(100))
    prospects = db.relationship('prospects', backref='referrers', lazy='dynamic')

    def dictifyFields(self):
        objToDict = {
            "id": self.id,
            "name": self.name,
            "industry": self.city,
        }
        return objToDict

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

def dictifyObjList(objList, end, ptr, outList):
    #function takes a list of object via objList, and returns a list of
    #dictionary kwargs in outList (made by calling the table's dictifyFields method)
    if ptr == end: #then end of list reached, return list value
        return outList
    else:
        outList.append(objList[ptr].dictifyFields()) #append dictified object fields
        return dictifyObjList(objList,end, ptr+1, outList)

#//START OF FLASK APP ROUTES
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
        newEntry = prospects(**request.json)
        db.session.add(newEntry)
        db.session.commit()
        prospectResponse = newEntry.dictifyFields()
        response = {
            "added": prospectResponse,
            "status": "added",
        }
        return jsonify(response),201

@app.route("/jhf/api/v1.0/prospects/find", methods=["POST"])
#THE API FOR RETURNING MULTIPLE RESULTS OF A QUERY - THE ONE BELOW CONSTRAINS RESULTS TO ONE!
def find_prospects(): #this api finds a prospect from the info posted and returns
    if request.method == "POST": #don't need this as there is a strict post method only in declaration
        if "dob" in request.json and request.json["dob"] is not "": #then format it ahead of time
            request.json["dob"] = datetime.strptime(request.json["dob"], "%d/%m/%Y").date()
        #Now make a dict to keep the sent **kwargs for the query
        searchFields = {} #empty dictionary
        for searchKeys in request.json: #make a dict of actual included search strings
            if request.json[searchKeys] is not "" and searchKeys != "scalar":
                searchFields[searchKeys] = request.json[searchKeys]
        queryResult = prospects.query.filter_by(**searchFields).all() #the query
        if queryResult != []:
            queryFound = "Found" #for respone
            responeStatus = 200
            if request.json["scalar"] == 1: #then user only wants first result
                queryResult = [queryResult.pop(0)] #take the first result and put in list
        else: #the query returned no result
            queryFound = "Not Found"
            responeStatus = 404
        #Now condition and shape the output
        jsonResult = []
        dictifyObjList(queryResult, len(queryResult), 0, jsonResult)
        #Now build the output
        respone = {
            "result": jsonResult,
            "length": len(jsonResult),
            "query": queryFound,
        }
        return jsonify(respone), responeStatus
    else: #not a POST request
        abort(404)

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
        #else #the method is DELETE
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
        objSort =[]
        objSorted = [] #list that will eventually hold the sorted gb details data
        if "specificTables" in request.json: #then there is a request for only specific tables' data
            if isinstance(request.json["specificTables"], list): #then proper format
                #check table matches in sent specifics of what was sent
                returnedTables = list(filter(lambda x: x in tableAddrs, request.json["specificTables"]))
                if returnedTables == []:
                    return jsonify("please enter proper table names all in small caps"), 400
                #else all good, search and return results from tables in returnedTables
                objLists = [tableAddrs[x].query.filter_by(prospects=owner).all() for x in returnedTables]
                #need to solve the case where the reponse is scalar (only one object not a list of them)!!!!
        else: #the user just wants  gn detailsin all tables about the owner sent back
            #get queries from all of the tables
            returnedTables = [x for x in tableAddrs] #just puts all table names in the list
            objLists = [tableAddrs[x].query.filter_by(prospects=owner).all() for x in tableAddrs]
        #Now prepare the output JSON
        #First condition gn details
        for tables in objLists:
            objSorted.append(dictifyObjList(tables, len(tables), 0, objSort))
            objSort = [] #clear the list in order to separate the list of objs from different tables
        gnDetails = {}
        #now make a dictionary for gn details
        for x in returnedTables:
            gnDetails[x] = objSorted.pop(0)
        #And now condition the rest of the JSON
        returnJSON = {
            "found": "true",
            "prospect": owner.dictifyFields(),
            "gnDetails": gnDetails,
        }
        return jsonify(returnJSON), 200
    else:
        abort(400)

if __name__ == "__main__":
    app.run(debug=True)
