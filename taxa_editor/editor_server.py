import json
from flask import Flask, render_template, Response, request, jsonify
# run with: python -m flask --app editor_server run
# Note: You will have to install flask (e.g., run "pip install flask")

from flask_sock import Sock
# Note: You will have to install flask (e.g., run "pip install flask_sock")

import asyncio
import sys
from asyncio.subprocess import PIPE, STDOUT
import subprocess
import os

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
sock = Sock(app)


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
        return jsonify({"error": str(e), "taxonName": lowCaseTaxonName})
    
@app.route("/getProcessedTaxon")
def getProcessedTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        return jsonify(json.loads(f.read()))
    except Exception as e:
        return jsonify({"error": str(e), "taxonName": lowCaseTaxonName})


@app.route("/saveTaxon", methods = ["POST"])
def postProcessedTaxon():
    taxonData = request.json
    lowCaseTaxonName = taxonData["name"].lower()

    taxonInfoString = json.dumps(taxonData, separators=(',', ':'), indent=0, ensure_ascii=False)
    f = open("../docs/taxa_source/" + lowCaseTaxonName + ".json", "w", encoding="utf-8")
    f.write(taxonInfoString)
    f.close()
    
    return jsonify({"status": "success"})


terminalWs = False
@sock.route('/terminal')
def terminal(ws):
    global terminalWs

    terminalWs = ws
    terminalWs.send(json.dumps({"type": "success"}))
    while True:
        data = ws.receive()
        if data == 'close':
            break
        ws.send(data)


loop = None

class SubprocessProtocol(asyncio.SubprocessProtocol):
    def pipe_data_received(self, fd, data):
        global terminalWs
        if fd == 1: # got stdout data (bytes)
            print(data.decode("utf-8"))
            terminalWs.send(json.dumps({"type": "cl", "line": str(data.decode("utf-8"))}))

    def connection_lost(self, exc):
        
        loop.stop() # end loop.run_forever()

def runProcessTaxa():
    global loop
    if os.name == 'nt':
        loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(loop.subprocess_exec(SubprocessProtocol, 
            "python", "process_taxa.py", cwd ="..", env={'PYTHONUNBUFFERED': '1'}))
        loop.run_forever()
    finally:
        loop.close()


@app.route("/processTaxa", methods = ["POST"])
def processTaxa():
    #asyncio.run(runProcessTaxa())
    runProcessTaxa()
    return json.dumps({"status": "started"})


