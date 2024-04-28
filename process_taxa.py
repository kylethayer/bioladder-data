import json, os

# load all data
taxaInfo = {}

taxaFiles = os.listdir("taxa_processed")

for taxonFile in taxaFiles:
    print("loading " + taxonFile)
    f = open("taxa_processed/" + taxonFile, encoding="utf-8")
    taxonInfo = json.loads(f.read())
    taxaInfo[taxonInfo["name"]] = taxonInfo 


# Find all subtaxa
for taxonName in taxaInfo:
    print("processing taxon " + taxonName)
    taxonInfo = taxaInfo[taxonName]
    # find all subtaxa
    subtaxa = []
    for potentialSubtaxonName in taxaInfo:
        potentialSubtaxonInfo = taxaInfo[potentialSubtaxonName]
        if(potentialSubtaxonInfo["parentTaxon"].lower() == taxonName.lower()):
            subtaxa.append(potentialSubtaxonName.lower())
        
    taxonInfo["subtaxa"] = subtaxa


# Output all files
for taxonName in taxaInfo:
    print("saving " + taxonName)
    taxonInfoString = json.dumps(taxaInfo[taxonName], separators=(',', ':'))
    f = open("taxa_processed/" + taxonName.lower() + ".json", "w", encoding="utf-8")
    f.write(taxonInfoString)
    f.close()

