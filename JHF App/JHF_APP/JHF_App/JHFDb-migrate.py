from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:jkl64fds@localhost:3306/jhf_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db  = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

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

class expenditures(db.Model):
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
    referrer_id = db.Column(db.Integer, db.ForeignKey('referrers.id'))
    constributions = db.relationship('contributions', backref='prospects', lazy='dynamic')
    notes = db.relationship('notes', backref='prospects', lazy='dynamic')
    #setup one-to-one relationship below
    expenditures = db.relationship('expenditures', backref='prospects',uselist=False)
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

if __name__ == '__main__':
    manager.run()
