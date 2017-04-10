from flask import Flask, render_template, request, url_for, jsonify, abort
from UserDbConfig import prospects, referrers

app = Flask(__name__)

new_entry = prospects("Paul", "Fitz", "60")
db.session.add(new_entry)
db.session.commit()
