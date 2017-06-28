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

def jsonTableAndObjs(tableList, objList):
    #takes a list of the tables, and a list of lists of objs [[obj, obj], [obj]]
    #with tableList and objList arranged in order of table ownership
    return [outputTableAndObjs(tableList[x])(objList[x]) for x in range(len(tableList))]

def outputTableAndObjs(table):
    #takes table name and in the sub func the object list, then
    #outputs the {table: [{...}, {...}]}
    def objToOutput(objList):
        if len(objList) == 0:
            return [] #return an empty list as an empty one was sent
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

def fieldValidation(vDict):
    def validateData(data):
        return [fieldCheck(vDict[field], data[field]) for field in data if field in vDict]
    return validateData

def digestAndExecute(fHandle, breakList):
    #receives a function handle/address, and a list of any item type that
    #needs to be individually passed to a function via its handle fHandle
    #will flatten the response so as to not return an overly nested list
    response = [fHandle(x) for x in breakList]
    return flattenListOfLists(response)

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

def getOwnerData(classAddr, **filterKwargs):
    # return(str(classAddr))
    data = classAddr.query.filter_by(**filterKwargs).all()
    if not isinstance(data, list): #if it's a single result, place single obj in list
        return [data]
    elif data == None: #i.e. there is no data, then return empty string
        return []
    return data #if not the above it's a list of objs so just return

def flattenListOfLists(listOfLists):
    #takes in a list of lists [[x],[x],[x]] and outputs a flat list of items
    #from the sublists [x,x,x]
    return [x for sublist in listOfLists for x in sublist]

def deleteObjs(flatObjList):
    #takes in a flat list of objects [obj, obj, obj]
    #deletes them and returns True
    [db.session.delete(obj) for obj in flatObjList]
    return True

def getDictKeys(dict):
    #takes in an arbitrary list of dicts and returns the keys in each of the
    # dicts. May get a list containing nested dicts, but will only return the keys
    #of the top layer of dicts (e.g [{key1: [{-},{-}]}, {key2: [{-}]}}] key1 & key2 returned)
    return [keys for data in dict for keys in data]

def filterEmptyLists(listOfLists):
    #takes a list of lists and returns only the nested lists that are not empty
    return [x for x in listOfLists if len(x)>0]

def newRows(classAddr, dataList, owner):
    #takes the memory address of the table class and a list of data in dicts,
    #(can be one dict in the list), and returns the handles of the new rows
    #in a list
    return [classAddr(**data, prospects=owner) for data in dataList]

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
        if target is not None:
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
        else:
            abort(404)

@app.route("/jhf/api/v1.0/prospects/gndetails/<int:prosp_id>", methods=["POST", "PUT", "DELETE"]) #the api for updating/adding/deleting prospects Gn Details
def prospect_gndetails(prosp_id):
    if prosp_id is not None:
        owner = prospects.query.get(prosp_id) #put the right prospect into the owner object
        if owner == None: #then there is no prospect that exist with this ID so abort
            return("Prospect does not exist"), 400
        #Else build ObbjDict below that stores class memory locations and info on required and constrained cols
        #if the column is a key in the tables key area then it has prescribed values (if a list), or is required if not
        objDict = {"expenditures": [{"classAddr": expenditures, "currentspend": "required", "goldenspend": "required"}],
            "assets": [{"classAddr": assets, "atype": ["Property", "Pension", "Investment", "Fixed"]}],
            "contributions": [{"classAddr": contributions, "ctype": ["Monthly", "Annual", "Lump Sum", "Final Salary"]}],
            "interests": [{"classAddr": interests, "itype": ["Service", "Purchase"]}],
            "notes": [{"classAddr": notes, "ntype": ["Private", "Public"]}]}
        if "data" in request.json:
            jsonData = request.json["data"] #handle for list of sent data items
        else:
            abort(400) #bad request as json format was not sent as needed
        if request.method == "POST":
            tableList = getDictKeys(jsonData) #get involved/sent tables in list
            dataList = [jsonData[x][tableList[x]] for x in range(len(tableList))] #get the corresponding data into a list in table order
            #VALIDATION
            #now validate fields based on the conditions in the objDict above
            validateCheck = [digestAndExecute(fieldValidation(objDict[y][0]), dataList[x]) for y in tableList for x in range(len(tableList))]
            flatValidateCheck = flattenListOfLists(validateCheck)
            if False in flatValidateCheck: #then one of the received data is not fit for entry
                return jsonify({"status": "failed", "operation": "add", "data": "invalid entries"})
            #expenditures table as one-to-one relatioinship with prospects so check we're not trying to create multiple
            if "expenditures" in tableList and owner.expenditures is not None:
                return jsonify({"status": "failed", "operation": "add", "data": "this prospect already has information on current and golden expenditure"})
            #CREATE AND ENTER THE NEW ROWS
            rowHandles = [newRows(objDict[table][0]["classAddr"], dataList[tableData], owner) for table, tableData in zip(tableList, range(len(dataList)))]
            #now flatten row handles prior to add an commit
            flatRowHandles = flattenListOfLists(rowHandles)
            # ownedHandles = addOwner(owner, flatRowHandles)
            [db.session.add(x) for x in flatRowHandles] #add new rows
            db.session.commit() #commit new rows
            #NOW OUTPUT NEW ROWS
            addedDetails = [outputTableAndObjs(tableList[x])(rowHandles[x]) for x in range(len(tableList))]
            returnJSON = {
                "status": "success",
                "operation": "create",
                "data": addedDetails,
            }
            return jsonify(returnJSON), 200
        elif request.method == "PUT": #then update API called
            #first check all records to be updated belong to the prospect whose prosp_id was sent in the requet's URL
            validOwner = [validateOwner(jsonData[table],objDict[table][0]["classaddr"], "prospect_id", prosp_id)
                for table in jsonData]
            if False in validOwner[0]: #then invalid
                return jsonify({"error": "not all sent fields belong to prospect ID"})
            #NOW VALIDATE THE FIELD ENTRIES
            validFields = [validateFields(objDict[table][0],record) for table in jsonData for record in jsonData[table]]
            validFieldsSearch = flattenListOfLists(validFields) #perform this to flatten the list of lists creates by validateFields
            if False in validFieldsSearch:
                return jsonify({"error": "certain fields have invalid values"})
            #now update the fields and get the handles
            updateHandles = [updateRecordList(objDict[table][0]["classaddr"], jsonData[table]) for table in jsonData]
            if False in updateHandles:
                return jsonify({"error": "certain field names in the passes records are incorrect"})
            [db.session.add(recordHandle) for recordHandle in updateHandles[0]]
            db.session.commit() #commit the updates
            #change dictionaries to objects
            ObjectsInList = [dictListToObj(objDict[table][0]["classaddr"],jsonData[table]) for table in jsonData]
            #now put them into output form
            tables = [x for x in jsonData] #put list of tables into a list (the length of which can be ascertained)
            updatedGnDetails = [outputTableAndObjs(tables[x])(ObjectsInList[x]) for x in range(len(tables))]
            returnJSON = {
                "status": "success",
                "operation": "update",
                "data": updatedGnDetails,
            }
            return jsonify(returnJSON), 200
        elif request.method == "DELETE":
            if request.get_json(silent = True) is None: #then good we received nothing as demanded so continue
                #having silent = True above prevents an error if there request is None
                #first fetch all data owned by the prosp_id
                ownerKwarg = {"prospect_id":prosp_id}
                ownerData = [getOwnerData(objDict[x][0]["classaddr"], **ownerKwarg) for x in objDict]
                # return(str(ownerData))
                filteredOwnerData = [x for x in ownerData if len(x) > 0]
                if len(filteredOwnerData) == 0: #then exit as there are no records to delete
                    return jsonify("this prospect has no Golden Number details to delete")
                #prep for output then, then flatten and delete
                tableList = [x for x in objDict] #create list of tables
                deletedData = [outputTableAndObjs(tableList[x])(ownerData[x]) for x in range(len(tableList))]
                filteredDeletedData = [x for x in deletedData if not isinstance(x,list)]
                #now delete owner's data
                toDelete = flattenListOfLists(filteredOwnerData) #condition to just get a list of objects
                # return (str(filteredOwnerData))
                [db.session.delete(x) for x in toDelete] #goes through and delete's
                db.session.commit() #commit the changes
                #return info to user
                returnJSON = {
                    "status": "success",
                    "operation": "delete",
                    "data": filteredDeletedData,
                }
                return jsonify(returnJSON), 200
            else:
                abort(400)
    else:
        abort(405)

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
        detailsFound = jsonTableAndObjs(returnedTables, objLists)
        #now take out any empty lists (indicating there is no data for that table)
        filteredDetailsFound = filterEmptyLists(detailsFound)
        #And now output data
        returnJSON = {
            "status": "success",
            "operation": "search",
            "prospect": owner.dictifyFields(),
            "gnDetails": filteredDetailsFound,
        }
        return jsonify(returnJSON), 200
    else:
        abort(405)

#THE SELECT DELETE API FOR GN DETAILS
@app.route("/jhf/api/v1.0/prospects/gndetails/selectdelete/<int:prosp_id>", methods=["DELETE"])
def selectDelete_gnDetails(prosp_id):
    if prosp_id is not None:
        #populate table of class addresses
        classAddr = {"expenditures": expenditures, "assets": assets, "contributions": contributions, "interests": interests, "notes": notes}
        jsonData = request.json["delete"]
        #Get list of tables first
        tableList = getDictKeys(jsonData)
        #now format list of data dictionaries
        kwargData = [jsonData[x][tableList[x]] for x in range(len(tableList))]
        #turn dicts into objects
        objList = [dictListToObj(classAddr[x], y) for x,y in zip(tableList, kwargData)]
        #now first of all produce list of JSON ordered list of deletedData for JSON output
        deletedJsonData = jsonTableAndObjs(tableList,objList)
        #now delete the objects before output
        # return(str(objList))
        toDelete = flattenListOfLists(objList)
        deleted = deleteObjs(toDelete)
        if deleted == True:
            db.session.commit()
            returnJSON = {
                "status": "success",
                "operation": "delete",
                "data": deletedJsonData,
            }
            return jsonify(returnJSON), 200
        else:
            abort(400)
    else:
        abort(400)

if __name__ == "__main__":
    app.run(debug=True)
