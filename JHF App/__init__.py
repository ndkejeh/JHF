from flask import Flask, render_template, request, url_for, jsonify, abort
from UserDbConfig import db, prospects, referrers

app = Flask(__name__)

@app.route("/")
def index():
    return  render_template("index.html")

@app.route("/adduser")
def adduser():
    return render_template("newuser.html")

@app.route("/jhf/api/v1.0/users", methods=["GET", "POST"]) #this will be the api for add user
def submitted():
    if request.method == 'POST':
        if not request.is_json:
            abort(400) #data sent wasn't JSON so about with an error else process

        #new_entry = prospects(request.json["FirstName"], request.json["Surname"], request.json["Retirement"])
        #db.session.add(new_entry)
        #db.session.commit()
        #return "Done" #jsonify( {"New Prospect" : new_entry} ),201 #201 is HTTP code for created
        #req = request.get_json
        #new_entry = prospects(request.form["fname"], request.form["lname"], request.form["retirement_age"])
        #db.session.add(new_entry)
        #db.session.commit()
        #return jsonify( {"New Prospect" : new_entry} ),201 #201 is HTTP code for created
        return "Is it JSON? %s" % request.is_json
    else:
        return "It's likely a GET submission!"
    #You then need the request method to access the data
    #request.form['firstname']

if __name__ == "__main__":
    app.run(debug=True)
