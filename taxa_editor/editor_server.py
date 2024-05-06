from flask import Flask, render_template, Response
# run with: python -m flask --app editor_server run
# Note: You will have to install flask (e.g., run "pip inistall flask")
app = Flask(__name__)

@app.route("/")
def home():
    f = open("./index.html")
    return f.read()

@app.route("/index.js")
def indexjs():
    f = open("./index.js")
    return Response(f.read(), mimetype='text/javascript')


# TODO: option to run process_taxa.py


