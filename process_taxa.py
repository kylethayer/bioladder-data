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
        taxonInfoString = json.dumps(taxonProcessedInfo, separators=(',', ':'), ensure_ascii=False).encode('utf8')
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
    taxaInfo[taxonInfo["name"].lower()] = taxonInfo 
    if taxonInfo.get("needs_to_be_processed"):
        taxaForProcessing[taxonInfo["name"].lower()] = True

counter = 0
# Find all subtaxa
for taxonName in taxaInfo:
    if(counter % 1000 == 0):
        print("loading all info (including subtaxa) for taxon " + taxonName)
    counter += 1

    
    taxonInfo = taxaInfo[taxonName.lower()]
    # find all subtaxa
    subtaxa = []
    for potentialSubtaxonName in taxaInfo:
        potentialSubtaxonInfo = taxaInfo[potentialSubtaxonName.lower()]
        if(potentialSubtaxonInfo["parentTaxon"].lower() == taxonName.lower()):
            subtaxa.append(potentialSubtaxonName.lower())
    
    if "subtaxa" in taxonInfo and taxonInfo["subtaxa"].sort() != subtaxa.sort():
        print("**Updating subtaxa for " + taxonName)
        taxonInfo["subtaxa"] = subtaxa
        taxaForProcessing[taxonName.lower()] = True
        taxaForSaving[taxonName.lower()] = True

#######################################
## process popularSubtaxa and popularAncestors
WeightAgainstBranchFraction = 0.7 # for popularSubtaxa, try to prevent too many from same branch
AncestorPopWeight = 0.85 # For popular ancestors, weight slightly toward picking up closer ancestors

def getPopularity(taxonName):
    if(not taxonName): # taxonName is null 
        return 0
    taxonInfo = taxaInfo[taxonName.lower()]
    taxonPopularity = taxonInfo["popularity"]
    if(not taxonPopularity): # popularity is ""
        return 0
    return taxonPopularity

while len(taxaForProcessing.keys())> 0:
    taxonName = list(taxaForProcessing.keys())[0]
    print("processing taxon: " + taxonName)
    
    taxonInfo = taxaInfo[taxonName.lower()]

    #####
    #Popular Ancestors
    #given parent popular ancestors and parent popularity, does parent go into the current taxon's popular ancestor list?
    
    # where we will save our newly updated info
    popAncestorNames = [None, None, None, None]
    popAncestorPops = [None, None, None, None]
    
    parentTaxon = taxonInfo["parentTaxon"]
    if(parentTaxon and parentTaxon != ""):
        parentTaxonInfo = taxaInfo[parentTaxon.lower()]
        parentPopularity = parentTaxonInfo["popularity"] # may be ""
        if not parentPopularity:
            parentPopularity = 0

        # start with copying the parent lists and update them
        parentPopAncestorNames = parentTaxonInfo["popularAncestors"] # values may be null
        popAncestorNames = parentPopAncestorNames[:] # make a clone of the names list
        popAncestorPops = list(map(getPopularity, parentPopAncestorNames))

        print(type(popAncestorPops))
        print(str(popAncestorPops))

        #Now see if it deserves a spot on the list
        if(  parentPopularity > popAncestorPops[0] * (AncestorPopWeight ** 3) or
 	     parentPopularity > popAncestorPops[1] * (AncestorPopWeight ** 2) or
          parentPopularity > popAncestorPops[2] * (AncestorPopWeight ** 1) or	   
 	     parentPopularity > popAncestorPops[3] or not popAncestorNames[3]):
            #We now will put parent in the ancestor[0] spot. 
            #See if Ancestor[0] should go into Ancestor[1] (each level works similarly)
            if(  popAncestorPops[0] > popAncestorPops[1] * (AncestorPopWeight ** 2) or
                popAncestorPops[0] > popAncestorPops[2] * (AncestorPopWeight ** 1) or
     	        popAncestorPops[0] > popAncestorPops[3] or not popAncestorNames[3]):
		  
                if(  popAncestorPops[1] > popAncestorPops[2] * (AncestorPopWeight ** 1) or
                    popAncestorPops[1] > popAncestorPops[3] or not popAncestorNames[3]):
			
                    if(popAncestorPops[2] > popAncestorPops[3] or not popAncestorNames[3]):
                        popAncestorNames[3] = popAncestorNames[2]
                        popAncestorPops[3] = popAncestorPops[2]
                    popAncestorNames[2] = popAncestorNames[1]
                    popAncestorPops[2] = popAncestorPops[1]
                popAncestorNames[1] = popAncestorNames[0]
                popAncestorPops[1] = popAncestorPops[0]
            popAncestorNames[0] = parentTaxon
            popAncestorPops[0] = parentPopularity

    # check and see if our newly calculated popAncestorNames or popAncestorPops
    # are different from what is currently saved
    if(popAncestorNames != taxonInfo["popularAncestors"] or
       popAncestorPops != taxonInfo["popularAncestorPops"] ):
        taxaForSaving[taxonName.lower()] = True
        
        # mark children as needing update if there was a change

        if("subtaxa" in taxonInfo):
            for subtaxonName in taxonInfo["subtaxa"]:
                taxaForProcessing[subtaxonName.lower()] = True


    #####
    # Popular Subtaxa

    possiblePopSubtaxa = []
    newPopSubtaxa = []

    # Add children as possibilities (self as branch)
    # Add children's popular subtaxa as possibilities (the child we got them from as the branch)

    for childTaxon in taxonInfo["subtaxa"]:
        newPossibleSubtaxa = {
            "name": childTaxon,
            "popularity": taxaInfo[childTaxon.lower()]["popularity"],
            "relative_popularity": taxaInfo[childTaxon.lower()]["popularity"], #will change as we choose children from different branches
            "branch": childTaxon
        }
        if not newPossibleSubtaxa["relative_popularity"]: # might be ""
            newPossibleSubtaxa["relative_popularity"] = 0
        
        possiblePopSubtaxa.append(newPossibleSubtaxa)


        for childPopSubTaxon in taxaInfo[childTaxon.lower()]["popularSubtaxa"]:
            newPossibleSubtaxa = {
                "name": childPopSubTaxon,
                "popularity": taxaInfo[childPopSubTaxon.lower()]["popularity"],
                "relative_popularity": taxaInfo[childPopSubTaxon.lower()]["popularity"], #will change as we choose children from different branches
                "branch": childTaxon
            }
            if not newPossibleSubtaxa["relative_popularity"]: # might be ""
                newPossibleSubtaxa["relative_popularity"] = 0
            
            possiblePopSubtaxa.append(newPossibleSubtaxa)

    # Find what should be the three popular subtaxa
    for i in range(3):
        #sort possible popSubtaxa to get most popular entry
        if(len(possiblePopSubtaxa) > 0):
            print("going to sort ",  str(possiblePopSubtaxa))
            possiblePopSubtaxa = sorted(possiblePopSubtaxa, key=lambda x: x['relative_popularity'], reverse=True)
            print("sorted ",  str(possiblePopSubtaxa))

            newPopSubtaxon = possiblePopSubtaxa.pop()

            newPopSubtaxa.append(newPopSubtaxon)

            # weigh against the remaining possiblePopSubtaxa in that same branch
            for popSubtaxon in possiblePopSubtaxa:
                if(popSubtaxon['branch'] == newPopSubtaxon['branch']):
                    popSubtaxon['relative_popularity'] *= WeightAgainstBranchFraction


    # check if there was a change that needs to be saved
    # and mark parent as needing update if there was a change
    if(newPopSubtaxa != taxonInfo["popularSubtaxa"]):
        taxaForSaving[taxonName.lower()] = True
        
        # mark parent as needing update if there was a change

        if(taxonInfo["parentTaxon"]):
            taxaForProcessing[taxonInfo["parentTaxon"].lower()] = True


    # We are done processing this taxon, mark as complete
    del taxonInfo["needs_to_be_processed"]
    del taxaForProcessing[taxonName]
    


######################################################3
# Output all files
for taxonName in taxaForSaving.keys():
    print("saving " + taxonName)
    taxonInfoString = json.dumps(taxaInfo[taxonName.lower()], separators=(',', ':'), indent=0, ensure_ascii=False).encode('utf8')
    print("prentending: ")
    #f = open("docs/taxa_processed/" + taxonName.lower() + ".json", "w", encoding="utf-8")
    #f.write(taxonInfoString)
    #f.close()

# TODO: update taxon_list.json and taxon_parent_summary.json
# Note: Taxon search could use a csv that has taxon name, other names, scientific name, and popularity
