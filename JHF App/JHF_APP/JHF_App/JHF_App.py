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

    def getFields(self):
        #returns the fields of this object as a list
        return["amount", "ctype", "cto"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["note", "ntype"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["currentspend", "goldenspend"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["name", "value", "atype"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["interest", "itype"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["fname", "lname", "dob", "retirement_age"]

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

    def getFields(self):
        #returns the fields of this object as a list
        return["name", "city", "industry"]

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

def dictListToObj(classAddr, dictList):
    #takes in a list of dictionaries that are fields for a table (that inc. "id" field),
    #and returns a list of these dictionary fields turned into their existing objects,
    #or None if the object does not exist
    getObject = dictToObj(classAddr)
    return [getObject(dict["id"]) for dict in dictList]

def dictToObj(obj):
    def getObj(id):
        return obj.query.get(id)
    return getObj

def tableAndObjs(table):
    #takes table name and in the sub func the object list, then
    #outputs the {table: [{...}, {...}]}
    def objToOutput(objList):
        return {table:[dictifyObj(obj) for obj in objList]}
    return objToOutput

def dictifyObj(obj):
    return obj.dictifyFields()

def dictifyObjList(objList, end, ptr, outList):
    #function takes a list of object via objList, and returns a list of
    #dictionary kwargs in outList (made by calling the table's dictifyFields method)
    if ptr == end: #then end of list reached, return list value
        return outList
    else:
        outList.append(objList[ptr].dictifyFields()) #append dictified object fields
        return dictifyObjList(objList,end, ptr+1, outList)

def fieldCheck(checks, fieldValue):
    #takes in a single field value and the validation check (either a list or string)
    #will return True if the value passes the validation check or false otherwise
    if isinstance(checks, list): #then check contains list of passable values
        if fieldValue not in checks: #then it is not an allowed value
            return False
    if fieldValue == "" or checks is None: #if not list it means it's a required field
        return False #because it's empty
    return True

def validateFields(vDict, recordList):
    #takes in a dictionary formatted for validation {"field1": ["setinput1", "setinput2"], "field2": "Required", etc.}
    #and returns table of true/false based on if the sent kwargs in recordList are valid for entry,
    #if there are no validation constraints (so fields are valid by default) an empty string is returned instead of falses
    return [fieldCheck(vDict[field], recordList[field]) for field in recordList if field in vDict]

def validateOwner(recordList, classAddr, forKey, owner):
    #takes in record list, foreign key, table object address, and owner (prosp_id)
    #and returns a list of Trues for each record that has owner as the FK, and False for each that does not.
    # recordObject = classAddr.query.get()
    return[ownerCheck(x,forKey, owner, classAddr) for x in recordList]

def ownerCheck(record, forKey, owner, classAddr):
    recordObject = classAddr.query.get(record["id"])
    if getattr(recordObject,forKey) == owner:
        return True
    return False
    #returns True or False based on whether

def updateTable(classAddr, recordList):
    #takes in a table object address and records to be updated and returns
    #a list of handles record handles to later add and commit if valid, or a false
    #value in the table if one is not valid
    validRecords = [classAddr.query.get(x["id"]) for x in recordList]
    if None in validRecords:
        return[False]
    return [x.updateRecord(**y) for x,y in zip(validRecords,recordList)]

def updateRecordList(classAddr, recordList):
    handle = updateRecord(classAddr)
    return [handle(record) for record in recordList]

def updateRecord(classAddr):
    #Parent function takes in a classAddr and makes a handle
    #child function takes in fields (which must include the id field that completes the parent handle)
    #and fetches the actual fields of the table in question for validation. After entering the valid
    #fields it returns the record's handle for it to be added and committed outside of the function
    def setUpdate(record):
        updateHandle = classAddr.query.get(record["id"])
        validFields = updateHandle.getFields()
        passedFields = list(filter(lambda x: x in validFields, record))
        if len(passedFields) == 0: #then error record's fields don't match those in this table
            return False
        holdVar = [setattr(updateHandle, field, record[field]) for field in passedFields]
        return updateHandle
    return setUpdate


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

@app.route("/jhf/api/v1.0/prospects/gndetails/<int:prosp_id>", methods=["POST", "PUT", "DELETE"]) #the api for updating/adding/deleting prospects Gn Details
def prospect_gndetails(prosp_id):
    if prosp_id is not None:
        owner = prospects.query.get(prosp_id) #put the right prospect into the owner object
        if owner == None: #then there is no prospect that exist with this ID so abort
            return("Prospect does not exist"), 400
        #Else build ObbjDict below that stores class memory locations and info on required and constrained cols
        #if the column is a key in the tables key area then it has prescribed values (if a list), or is required if not
        objDict = {"expenditures": [{"classaddr": expenditures, "currentspend": "required", "goldenspend": "required"}],
            "assets": [{"classaddr": assets, "atype": ["Property", "Pension", "Investment", "Fixed"]}],
            "contributions": [{"classaddr": contributions, "ctype": ["Monthly", "Annual", "Lump Sum", "Final Salary"]}],
            "interests": [{"classaddr": interests, "itype": ["Services", "Purchases"]}],
            "notes": [{"classaddr": notes, "ntype": ["Private", "Public"]}]}
        if request.method == "POST":
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
        elif request.method == "PUT": #then update API called
            tablesGroup = request.json["updates"]
            #first check all records to be updated belong to the prospect whose prosp_id was sent in the requet's URL
            validOwner = [validateOwner(tablesGroup[table],objDict[table][0]["classaddr"], "prospect_id", prosp_id)
                for table in tablesGroup]
            if False in validOwner[0]: #then invalid
                return jsonify({"error": "not all sent fields belong to prospect ID"})
            #NOW VALIDATE THE FIELD ENTRIES
            validFields = [validateFields(objDict[table][0],record) for table in tablesGroup for record in tablesGroup[table]]
            validFieldsSearch = [x for sublist in validFields for x in sublist] #perform this to flatten the list of lists creates by validateFields
            if False in validFieldsSearch:
                return jsonify({"error": "certain fields have invalid values"})
            #now update the fields and get the handles
            updateHandles = [updateRecordList(objDict[table][0]["classaddr"], tablesGroup[table]) for table in tablesGroup]
            return(str(updateHandles))
            if False in updateHandles:
                return jsonify({"error": "certain field names in the passes records are incorrect"})
            [db.session.add(recordHandle) for recordHandle in updateHandles[0]]
            db.session.commit() #commit the updates
            #change dictionaries to objects
            ObjectsInList = [dictListToObj(objDict[table][0]["classaddr"],tablesGroup[table]) for table in tablesGroup]
            #now put them into output form
            tables = [x for x in tablesGroup] #put list of tables into a list (the length of which can be ascertained)
            updatedGnDetails = [tableAndObjs(tables[x])(ObjectsInList[x]) for x in range(len(tables))]
            returnJSON = {
                "status": "success",
                "updates": updatedGnDetails.pop(0), #gndetails are enclosed in a list so pop out
            }
            return jsonify(returnJSON), 200
            # tableUpdates = [tableAdds(request.json[updates][x], objDict[x][0][classaddr],owner) for x in request.json[updates]]
            #[db.session.add(for ]
        #else #the method is DELETE
    else:
        abort(404)

#THE Gn Details SEARCH API
@app.route("/jhf/api/v1.0/prospects/gndetails/find/<int:prosp_id>", methods=["POST"]) #The API for searching prospects Gn Details
def searchProspectGndetails(prosp_id):
    if prosp_id is not None:
        owner = prospects.query.get(prosp_id)
        if owner == None: #then prospect doesn't exist abort
            return jsonify("Prospect does not exist"), 400
        tableAddrs = {"assets": assets, "contributions": contributions, "notes": notes,
            "expenditures": expenditures, "interests": interests} #dict of tables and their class addresses
        objSort =[]
        objSorted = [] #list that will eventually hold the sorted gn details data
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
            returnedTables = [x for x in tableAddrs] #just puts all table names in the list [potentially redundant]
            objLists = [tableAddrs[x].query.filter_by(prospects=owner).all() for x in tableAddrs]
        #Now prepare the output JSON
        #First condition gn details
        for list in objLists:
            objSorted.append(dictifyObjList(list, len(list), 0, objSort))
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
