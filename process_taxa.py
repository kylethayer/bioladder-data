import json, os


# copy any changes from taxa_source to taxa_processed
taxaSourceFiles = os.listdir("docs/taxa_source")

counter = 0

for taxonSourceFile in taxaSourceFiles:
    
    if(counter % 1000 == 0):
        print("copying over info for taxon " + taxonSourceFile)
    counter += 1

    f = open("docs/taxa_source/" + taxonSourceFile, encoding="utf-8")
    taxonSourceInfo = json.loads(f.read())

    taxonProcessedInfo = {}
    if(os.path.isfile("docs/taxa_processed/"+ taxonSourceFile)):
        f = open("docs/taxa_processed/"+ taxonSourceFile, encoding="utf-8")
        taxonProcessedInfo = json.loads(f.read())

    anyChanges = False
    for key, value in taxonSourceInfo.items():
        if(taxonProcessedInfo[key] != value):
            taxonProcessedInfo[key] = value
            anyChanges = True
    
    if(anyChanges):
        taxonProcessedInfo["needs_to_be_processed"] = True

        print("**saving updated version of file " + taxonSourceFile)
        taxonInfoString = json.dumps(taxonProcessedInfo, separators=(',', ':'))
        f = open("docs/taxa_processed/" + taxonSourceFile, "w", encoding="utf-8")
        f.write(taxonInfoString)
        f.close()



# load all data
# TODO: Use ["needs_to_be_processed"] to skip ones that aren't changed or don't need to be processed

taxaInfo = {}

taxaForProcessing = {}
taxaForSaving = {}

taxaFiles = os.listdir("docs/taxa_processed")


counter = 0
for taxonFile in taxaFiles:
    if(counter % 1000 == 0):
        print("loading for processing" + taxonFile)
    counter += 1
    
    f = open("docs/taxa_processed/" + taxonFile, encoding="utf-8")
    taxonInfo = json.loads(f.read())
    taxaInfo[taxonInfo["name"]] = taxonInfo 
    if taxonInfo.get("needs_to_be_processed"):
        taxaForProcessing[taxonInfo["name"]] = True

counter = 0
# Find all subtaxa
for taxonName in taxaInfo:
    if(counter % 1000 == 0):
        print("processing taxon " + taxonName)
    counter += 1

    
    taxonInfo = taxaInfo[taxonName]
    # find all subtaxa
    subtaxa = []
    for potentialSubtaxonName in taxaInfo:
        potentialSubtaxonInfo = taxaInfo[potentialSubtaxonName]
        if(potentialSubtaxonInfo["parentTaxon"].lower() == taxonName.lower()):
            subtaxa.append(potentialSubtaxonName.lower())
    
    if "subtaxa" in taxonInfo and taxonInfo["subtaxa"].sort() != subtaxa.sort():
        print("**Updating subtaxa for " + taxonName)
        taxonInfo["subtaxa"] = subtaxa
        taxaForProcessing[taxonName] = True
        taxaForSaving[taxonName] = True


# Output all files
for taxonName in taxaForSaving.keys():
    print("saving " + taxonName)
    taxonInfoString = json.dumps(taxaInfo[taxonName], separators=(',', ':'))
    f = open("docs/taxa_processed/" + taxonName.lower() + ".json", "w", encoding="utf-8")
    f.write(taxonInfoString)
    f.close()

# TODO: update taxon_list.json and taxon_parent_summary.json