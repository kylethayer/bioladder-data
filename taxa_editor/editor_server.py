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
    except Exception as e:
        return jsonify({"error": e, "taxonName": lowCaseTaxonName})
    
@app.route("/getProcessedTaxon")
def getProcessedTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        return jsonify(json.loads(f.read()))
    except Exception as e:
        return jsonify({"error": e, "taxonName": lowCaseTaxonName})


@app.route("/saveTaxon", methods = ["POST"])
def postProcessedTaxon():
    taxonData = request.json
    lowCaseTaxonName = taxonData["name"].lower()

    taxonInfoString = json.dumps(taxonData, separators=(',', ':'))
    f = open("../docs/taxa_source/" + lowCaseTaxonName + ".json", "w", encoding="utf-8")
    f.write(taxonInfoString)
    f.close()
    
    return jsonify({"status": "success"})



# TODO: option to run process_taxa.py


