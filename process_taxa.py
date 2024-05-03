import json, os


# copy any changes from taxa_source to taxa_processed
taxaSourceFiles = os.listdir("taxa_source")

for taxonSourceFile in taxaSourceFiles:
    f = open("taxa_source/" + taxonSourceFile, encoding="utf-8")
    taxonSourceInfo = json.loads(f.read())

    taxonProcessedInfo = {}
    if(os.path.isfile("taxa_processed/"+ taxonSourceFile)):
        f = open("taxa_processed/"+ taxonSourceFile, encoding="utf-8")
        taxonProcessedInfo = json.loads(f.read())

    anyChanges = False
    for key, value in taxonSourceInfo.items():
        if(taxonProcessedInfo[key] != value):
            taxonProcessedInfo[key] = value
            anyChanges = True
    
    if(anyChanges):
        taxonProcessedInfo["needs_to_be_processed"] = True

        print("saving updated version of file " + taxonSourceFile)
        taxonInfoString = json.dumps(taxonSourceInfo, separators=(',', ':'))
        f = open("taxa_processed/" + taxonSourceFile, "w", encoding="utf-8")
        f.write(taxonInfoString)
        f.close()



# load all data
# TODO: Use ["needs_to_be_processed"] to skip ones that aren't changed or don't need to be processed

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

