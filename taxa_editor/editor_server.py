import json
from flask import Flask, render_template, Response, request, jsonify
# run with: python -m flask --app editor_server run
# Note: You will have to install flask (e.g., run "pip install flask")
app = Flask(__name__)

@app.route("/")
def home():
    f = open("./index.html")
    return f.read()

@app.route("/index.js")
def indexjs():
    f = open("./index.js")
    return Response(f.read(), mimetype='text/javascript')

@app.route("/getTaxon")
def getTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_source/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_source/" + lowCaseTaxonName + ".json")
        return jsonify(json.loads(f.read()))
    except:
        return jsonify({"error": "file not found"})
    
@app.route("/getProcessedTaxon")
def getProcessedTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        return jsonify(json.loads(f.read()))
    except:
        return jsonify({"error": "file not found"})
    



# TODO: option to run process_taxa.py


