import json, os, requests, time
# you need to install requests ("pip install requests")


# Do several audits, looking for:
# - Missing parent Taxa (except Life)
# - broken wikipedia images


# Load all source taxa
taxaInfo = {}

taxaFiles = os.listdir("docs/taxa_source")

counter = 0
for taxonFile in taxaFiles:
    if(counter % 1000 == 0):
        print("loading for processing" + taxonFile)
    counter += 1
    
    f = open("docs/taxa_source/" + taxonFile, encoding="utf-8")
    taxonInfo = json.loads(f.read())
    taxaInfo[taxonInfo["name"].lower()] = taxonInfo 

#### make sure all have a parent (except life)
counter = 0
# Find all subtaxa
for taxonName in taxaInfo:
    if(counter % 1000 == 0):
        print("checking parent taxon for " + taxonName)
    counter += 1

    taxonInfo = taxaInfo[taxonName.lower()]
    parentTaxon = taxonInfo["parentTaxon"]
    if(not parentTaxon or "parentTaxon" not in taxonInfo):
        if(taxonName.lower() != "life"):
            print("**** Missing parent "+ parentTaxon +" for " + taxonName)


#### check wikipedia images
counter = 0
# Find all subtaxa
for taxonName in taxaInfo:
    if(counter % 100 == 0):
        print("checking image file for " + taxonName)
    counter += 1

    taxonInfo = taxaInfo[taxonName.lower()]
    wikiImage = taxonInfo["wikipediaImg"]
    if(wikiImage):
        try:
            r = requests.get(wikiImage, timeout = 5)
            if(r.status_code > 200):
                time.sleep(5) # retry one after one second
                r = requests.get(wikiImage, timeout = 5)
                if(r.status_code > 200):
                    time.sleep(10) # retry 2 after three seconds
                    r = requests.get(wikiImage, timeout = 5)
                    if(r.status_code > 200):
                        print("*** Error loading '" + taxonName + "' (" + str(r.status_code) + ")")
                        print("   - url: "+ wikiImage)
                        if(r.status_code == 403):
                            time.sleep(60)
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print("error loading image for " + taxonName)
            print (e)