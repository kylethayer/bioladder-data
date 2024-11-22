import json, re
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
    f = open("./index.js", encoding="utf-8")
    return Response(f.read(), mimetype='text/javascript')

@app.route("/getTaxon")
def getTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_source/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_source/" + lowCaseTaxonName + ".json", encoding="utf-8")
        return jsonify(json.loads(f.read()))
    except Exception as e:
        return jsonify({"error": str(e), "taxonName": lowCaseTaxonName})
    
@app.route("/getProcessedTaxon")
def getProcessedTaxon():
    taxonName = request.args.get('taxonName')
    lowCaseTaxonName = taxonName.lower()
    try:
        print("loading " + "../docs/taxa_processed/" + lowCaseTaxonName + ".json")
        f = open("../docs/taxa_processed/" + lowCaseTaxonName + ".json", encoding="utf-8")
        return jsonify(json.loads(f.read()))
    except Exception as e:
        return jsonify({"error": str(e), "taxonName": lowCaseTaxonName})


@app.route("/saveTaxon", methods = ["POST"])
def postProcessedTaxon():
    taxonData = request.json
    lowCaseTaxonName = taxonData["name"].lower()

    # make sure wiki image is 300px
    if(taxonData["wikipediaImg"]):
        taxonData["wikipediaImg"] = re.sub(r'\d+px-', "330px-", taxonData["wikipediaImg"])

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
    if(terminalWs != False):
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

    def error_received(self, exc): # This doesn't seem to catch errors
        terminalWs.send(json.dumps({"type": "cl", "line": "Error: " + str(exc)}))
        print('Error received:', exc)

    def connection_lost(self, exc):
        terminalWs.send(json.dumps({"type": "cl", "line": "closed process connection " + str(exc) + "\n"}))
        loop.stop() # end loop.run_forever()

def runProcessCommand(pythonScriptName):
    global loop
    global terminalWs
    if os.name == 'nt':
        loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    try:
        # This doesn't seem to catch errors
        # loop.set_exception_handler(lambda loop, context : terminalWs.send(json.dumps({"type": "cl", "line": "process error + " + str(context.get('exception')) + " \n"})))
        
        loop.run_until_complete(loop.subprocess_exec(SubprocessProtocol, 
            "python", pythonScriptName, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            cwd ="..", env={'PYTHONUNBUFFERED': '1'}))
        loop.run_forever()
    # except Exception as e: # This doesn't seem to catch errors
    #     terminalWs.send(json.dumps({"type": "cl", "line": "error " + str(e) + "\n"}))
    #     loop.close()
    finally:
        terminalWs.send(json.dumps({"type": "cl", "line": "process ended \n"}))
        loop.close()


@app.route("/processTaxa", methods = ["POST"])
def processTaxa():
    #asyncio.run(runProcessTaxa())
    runProcessCommand("process_taxa.py")
    return json.dumps({"status": "started"})



@app.route("/auditTaxa", methods = ["POST"])
def auditTaxa():
    #asyncio.run(runProcessTaxa())
    runProcessCommand("audit_taxa.py")
    return json.dumps({"status": "started"})


