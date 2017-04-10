from flask import Flask, render_template, request, url_for, jsonify, abort
from UserDbConfig import db, prospects, referrers

app = Flask(__name__)

@app.route("/")
def index():
    return  render_template("index.html")

@app.route("/adduser")
def adduser():
    return render_template("AddUserForm.html")

@app.route("/jhf/api/v1.0/users", methods=["GET", "POST"]) #this will be the api for add user
def submitted():
    if request.method == 'POST':
        if not request.json:
            abort(400) #data sent wasn't JSON so about with an error else process

        new_entry = prospects(request.json["fname"], request.json["lname"], request.json["retirement_age"])
        db.session.add(new_entry)
        db.session.commit()
        #return jsonify( {"New Prospect" : new_entry} ),201 #201 is HTTP code for created
        #req = request.get_json
        return new_entry.fname
    else:
        return "It's likely a GET submission!"
    #You then need the request method to access the data
    #request.form['firstname']

if __name__ == "__main__":
    app.run(debug=True)
