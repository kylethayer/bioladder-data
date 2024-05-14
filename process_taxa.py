import json, os, csv

print("start of process taxa")

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
        if(key not in taxonProcessedInfo or taxonProcessedInfo[key] != value):
            taxonProcessedInfo[key] = value
            anyChanges = True
    
    if(anyChanges):
        taxonProcessedInfo["needs_to_be_processed"] = True

        print("**saving updated version of file " + taxonSourceFile)
        taxonInfoString = json.dumps(taxonProcessedInfo, separators=(',', ':'), indent=0, ensure_ascii=False)
        f = open("docs/taxa_processed/" + taxonSourceFile, "w", encoding="utf-8")
        f.write(taxonInfoString)
        f.close()



# load all data
# TODO: Use ["needs_to_be_processed"] to skip ones that aren't changed or don't need to be processed

taxaInfo = {}

taxaForProcessing = {}
taxaForSaving = {}

taxaFiles = os.listdir("docs/taxa_processed")


def getMaxThisOrSubtaxaPopularity(taxonInfo):
    taxonMaxPopularity = -100
    if("popularity" in taxonInfo and taxonInfo["popularity"] != '' and taxonInfo["popularity"] != None 
        and taxonInfo["popularity"] > taxonMaxPopularity):
        taxonMaxPopularity = taxonInfo["popularity"]
    
    if("popularSubtaxa" in taxonInfo):
        for popSubtaxon in taxonInfo["popularSubtaxa"]:
            if("popularity" in taxaInfo[popSubtaxon] and taxaInfo[popSubtaxon]["popularity"] != '' and taxaInfo[popSubtaxon]["popularity"] != None 
               and taxaInfo[popSubtaxon]["popularity"] > taxonMaxPopularity):
                taxonMaxPopularity = taxaInfo[popSubtaxon]["popularity"]

    return taxonMaxPopularity
 

def subtaxonSortKey(subtaxonName):
    subtaxonInfo = taxaInfo[subtaxonName]
    # primary sort: max popularity in this branch
    primarySortKey = - getMaxThisOrSubtaxaPopularity(subtaxonInfo)
    #secondary sort: how many popular subtaxa (which maxes out at 3, but at least gives us a sense of if there is more down that path)
    secondarySortKey = - len(subtaxonInfo["popularSubtaxa"]) if "popularSubtaxa" in subtaxonInfo else 0
    #tertiary sort: name
    tertiarySortKey = subtaxonName.lower()

    return (primarySortKey, secondarySortKey, tertiarySortKey)

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
        # for initial needs_to_be_processed, add children and parent
        if("parentTaxon" in taxonInfo and taxonInfo["parentTaxon"] != ''):
            taxaForProcessing[taxonInfo["parentTaxon"].lower()] = True
        if("subtaxa" in taxonInfo):
            for subtaxonName in taxonInfo["subtaxa"]:
                taxaForProcessing[subtaxonName.lower()] = True

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

    sortedSubtaxa = sorted(subtaxa, key=subtaxonSortKey)

    ## Also, update sort at end of processing step below
    if "subtaxa" not in taxonInfo or taxonInfo["subtaxa"] != sortedSubtaxa:
        print("**Updating subtaxa for " + taxonName + " ( was "+str(taxonInfo["subtaxa"])+ " now " + str(sortedSubtaxa) + ")")
        taxonInfo["subtaxa"] = sortedSubtaxa

        print("--- adding to processing list '" + taxonName.lower() + "' since subtaxa updated 1")
        taxaForProcessing[taxonName.lower()] = True
        taxaForSaving[taxonName.lower()] = True

    # make sure popularAncestors in taxonInfo, even if blank
    if "popularAncestors" not in taxonInfo:
        taxonInfo["popularAncestors"] = [None, None, None, None]
        taxonInfo["popularAncestorPops"] = [None, None, None, None]

#######################################
## process popularSubtaxa and popularAncestors
WeightAgainstBranchFraction = 0.7 # for popularSubtaxa, try to prevent too many from same branch
AncestorPopWeight = 0.85 # For popular ancestors, weight slightly toward picking up closer ancestors

def getPopularity(taxonName):
    if(not taxonName): # taxonName is null 
        return ""
    
    if(taxonName not in taxaInfo):
        print("********WARNING**********")
        print("taxon " + taxonName + " does not exist (tried to look up popularity)")
        return -100

    taxonInfo = taxaInfo[taxonName.lower()]
    taxonPopularity = taxonInfo["popularity"]
    if(not taxonPopularity): # popularity is ""
        return ""
    return taxonPopularity

# Process Taxa until none left
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
        parentPopularityActual = parentPopularity
        if not parentPopularity:
            parentPopularity = 0

        # start with copying the parent lists and update them
        parentPopAncestorNames = parentTaxonInfo["popularAncestors"] # values may be null
        popAncestorNames = parentPopAncestorNames[:] # make a clone of the names list
        popAncestorPopsActual = list(map(getPopularity, parentPopAncestorNames))
        popAncestorPops = list(map(getPopularity, parentPopAncestorNames))
        popAncestorPops = list(map(lambda x: x if x else 0, popAncestorPops))

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
                        popAncestorPopsActual[3] = popAncestorPopsActual[2]
                    popAncestorNames[2] = popAncestorNames[1]
                    popAncestorPops[2] = popAncestorPops[1]
                    popAncestorPopsActual[2] = popAncestorPopsActual[1]
                popAncestorNames[1] = popAncestorNames[0]
                popAncestorPops[1] = popAncestorPops[0]
                popAncestorPopsActual[1] = popAncestorPopsActual[0]
            popAncestorNames[0] = parentTaxon
            popAncestorPops[0] = popAncestorPops
            popAncestorPopsActual[0] = parentPopularityActual

    # check and see if our newly calculated popAncestorNames or popAncestorPops
    # are different from what is currently saved
    if("popularAncestors" not in taxonInfo or 
        "popularAncestorPops" not in taxonInfo):
        print("updated missing pop ancestors " + taxonInfo["name"] + "--------------")
        taxonInfo["popularAncestors"] = popAncestorNames
        taxonInfo["popularAncestorPops"] = popAncestorPopsActual

        taxaForSaving[taxonName.lower()] = True

        # mark children as needing update since there was a change

        if("subtaxa" in taxonInfo):
            for subtaxonName in taxonInfo["subtaxa"]:
                print(" --- adding to processing list '" + subtaxonName.lower() + "' (since "+ taxonName +" no popularAncestors, now are)")
                print(" ---  - " + str(taxonInfo["popularAncestors"]))
                print(" ---  - " + str(taxonInfo["popularAncestorPops"]))
                taxaForProcessing[subtaxonName.lower()] = True

    elif(popAncestorNames != taxonInfo["popularAncestors"] or
            popAncestorPopsActual != taxonInfo["popularAncestorPops"] ):
        print("updated " + taxonInfo["name"] + "--------------")
        print(" ancestor was " + str(taxonInfo["popularAncestors"]))
        print(" ancestor now " + str(popAncestorNames))
        taxonInfo["popularAncestors"] = popAncestorNames
        print(" ancestor was " + str(taxonInfo["popularAncestorPops"]))
        print(" ancestor now " + str(popAncestorPopsActual))
        taxonInfo["popularAncestorPops"] = popAncestorPopsActual

        taxaForSaving[taxonName.lower()] = True
        
        # mark children as needing update if there was a change

        if("subtaxa" in taxonInfo):
            for subtaxonName in taxonInfo["subtaxa"]:
                print(" --- adding to processing list '" + subtaxonName.lower() + "'")
                taxaForProcessing[subtaxonName.lower()] = True


    #####
    # Popular Subtaxa

    possiblePopSubtaxa = []
    newPopSubtaxaInfo = []

    # Add children as possibilities (self as branch)
    # Add children's popular subtaxa as possibilities (the child we got them from as the branch)

    for childTaxon in taxonInfo["subtaxa"]:
        childTaxonInfo = taxaInfo[childTaxon.lower()]
        if "popularSubtaxa" not in childTaxonInfo:
            childTaxonInfo["popularSubtaxa"] = []

        newPossibleSubtaxa = {
            "name": childTaxon,
            "popularity":childTaxonInfo["popularity"],
            "relative_popularity": childTaxonInfo["popularity"], #will change as we choose children from different branches
            "branch": childTaxon,
            "branchBuddies": childTaxonInfo["popularSubtaxa"] #all popularSubtaxa are considered branch buddies
        }
        if not newPossibleSubtaxa["relative_popularity"]: # might be ""
            newPossibleSubtaxa["relative_popularity"] = 0
        
        possiblePopSubtaxa.append(newPossibleSubtaxa)



        sameBranchPairing = {}
        if "popularSubtaxaSameBranch" in childTaxonInfo and childTaxonInfo["popularSubtaxaSameBranch"]:
            sameBranchNums = childTaxonInfo["popularSubtaxaSameBranch"].split(",")
            sameBranchPairing = {
                childTaxonInfo["popularSubtaxa"][int(sameBranchNums[0])]: childTaxonInfo["popularSubtaxa"][int(sameBranchNums[1])],
                childTaxonInfo["popularSubtaxa"][int(sameBranchNums[1])]: childTaxonInfo["popularSubtaxa"][int(sameBranchNums[0])]
                }

        for childPopSubTaxon in childTaxonInfo["popularSubtaxa"]:
            newPossibleSubtaxa = {
                "name": childPopSubTaxon,
                "popularity": taxaInfo[childPopSubTaxon]["popularity"],
                "relative_popularity": taxaInfo[childPopSubTaxon]["popularity"], #will change as we choose children from different branches
                "branch": childTaxon.lower(),
                "branchBuddies": [sameBranchPairing[childPopSubTaxon] if childPopSubTaxon in sameBranchPairing else "",
                                  childTaxon.lower()] #the branch is also considered a close relative / branch buddy
            }
            if not newPossibleSubtaxa["relative_popularity"]: # might be ""
                newPossibleSubtaxa["relative_popularity"] = 0
            
            possiblePopSubtaxa.append(newPossibleSubtaxa)

    # Find what should be the three popular subtaxa
    for i in range(3):
        #sort possible popSubtaxa to get most popular entry
        if(len(possiblePopSubtaxa) > 0):
            #print("presorted: " + str(possiblePopSubtaxa))
            #sorted by relative popularity and name (should be deterministic)
            possiblePopSubtaxa = sorted(possiblePopSubtaxa, key=lambda x: (-x['relative_popularity'], x['name'].lower()))
            #print("sorted: " + str(possiblePopSubtaxa))

            newPopSubtaxon = possiblePopSubtaxa.pop(0)
            #print("newPopSubtaxon 1: " + str(newPopSubtaxon))

            newPopSubtaxaInfo.append(newPopSubtaxon)

            # weigh against the remaining possiblePopSubtaxa in that same branch
            for popSubtaxon in possiblePopSubtaxa:
                if(popSubtaxon['branch'] == newPopSubtaxon['branch']):
                    popSubtaxon['relative_popularity'] *= WeightAgainstBranchFraction
                    # further weight against any other popular subtaxon that was in the same branch within the inheretid popular descendents
                    if(popSubtaxon["name"].lower() in newPopSubtaxon['branchBuddies']):
                        popSubtaxon['relative_popularity'] *= WeightAgainstBranchFraction

    newPopSubtaxaInfo = sorted(newPopSubtaxaInfo, key=lambda x: ( 100 if not x['popularity'] else -x['popularity'], x['name'].lower())) #Note: popularity negative to sort highest popularity first
    newPopSubtaxa = list(map(lambda x: x['name'].lower(), newPopSubtaxaInfo))
    newPopularSubtaxaPops = list(map(lambda x: x['popularity'], newPopSubtaxaInfo))

    # Which two are closer in branches than the others
    newPopSubtaxaSameBranch = ""
    if(len(newPopSubtaxaInfo) == 3): # need 3 for this to be meaningful
        if(newPopSubtaxaInfo[0]["branch"] == newPopSubtaxaInfo[1]["branch"]): #maybe 0 and 1
            if(newPopSubtaxaInfo[0]["branch"] == newPopSubtaxaInfo[2]["branch"]): #all three are same, inherit
                #ALL THREE SAME, Inherit branch info
                branchInfo = taxaInfo[newPopSubtaxaInfo[0]["branch"]]
                if("popularSubtaxaSameBranch" in branchInfo and branchInfo["popularSubtaxaSameBranch"] != ""): # if it's empty, we already set ours as ""
                    branchPopSubtaxa = branchInfo["popularSubtaxa"]
                    if(set(branchPopSubtaxa) == set(newPopSubtaxa)):
                        inheretbranchPopSubtaxon1 = branchPopSubtaxa[int(branchInfo["popularSubtaxaSameBranch"].split(",")[0])]
                        inheretbranchPopSubtaxon2 = branchPopSubtaxa[int(branchInfo["popularSubtaxaSameBranch"].split(",")[1])]
                        newPopSubtaxaSameBranchNums = [newPopSubtaxa.index(inheretbranchPopSubtaxon1), newPopSubtaxa.index(inheretbranchPopSubtaxon2)]
                        newPopSubtaxaSameBranch = ",".join(str(i) for i in sorted(newPopSubtaxaSameBranchNums))
            else: #0 and 1 are closer!
                newPopSubtaxaSameBranch = "0,1"
        elif(newPopSubtaxaInfo[0]["branch"] == newPopSubtaxaInfo[2]["branch"]): # 0 and 2 (already checked for all three)
            newPopSubtaxaSameBranch = "0,2"
        elif(newPopSubtaxaInfo[1]["branch"] == newPopSubtaxaInfo[2]["branch"]): # 1 and 2 (already checked for all three)
            newPopSubtaxaSameBranch = "0,2"
        else: #all three different branches
            newPopSubtaxaSameBranch = ""

    # check if there was a change that needs to be saved
    # and mark parent as needing update if there was a change
    if("popularSubtaxa" not in taxonInfo or "popularSubtaxaPops" not in taxonInfo or "popularSubtaxaSameBranch" not in taxonInfo):
        print("add missing popularSubtaxa to " + taxonInfo["name"] + "--------------")
        taxonInfo["popularSubtaxa"] = newPopSubtaxa
        taxonInfo["popularSubtaxaPops"] = newPopularSubtaxaPops
        taxonInfo["popularSubtaxaSameBranch"] = newPopSubtaxaSameBranch

        taxaForSaving[taxonName.lower()] = True
        
        # mark parent as needing update if there was a change

        if(taxonInfo["parentTaxon"] and taxonInfo["parentTaxon"] != ''):
            print(" --- adding to processing list '" + taxonInfo["parentTaxon"].lower() + "'")
            taxaForProcessing[taxonInfo["parentTaxon"].lower()] = True
    if(newPopSubtaxa != taxonInfo["popularSubtaxa"] 
            or newPopularSubtaxaPops != taxonInfo["popularSubtaxaPops"]
            or newPopSubtaxaSameBranch != taxonInfo["popularSubtaxaSameBranch"]):
        print("updated " + taxonInfo["name"] + "--------------")
        print(" popsubtaxa was " + str(taxonInfo["popularSubtaxa"]))
        print(" popsubtaxa now " + str(newPopSubtaxa))
        taxonInfo["popularSubtaxa"] = newPopSubtaxa
        taxonInfo["popularSubtaxaPops"] = newPopularSubtaxaPops
        taxonInfo["popularSubtaxaSameBranch"] = newPopSubtaxaSameBranch

        taxaForSaving[taxonName.lower()] = True
        
        # mark parent as needing update if there was a change

        if(taxonInfo["parentTaxon"] and taxonInfo["parentTaxon"] != ''):
            print(" --- adding to processing list '" + taxonInfo["parentTaxon"].lower() + ' (parent taxon)')
            taxaForProcessing[taxonInfo["parentTaxon"].lower()] = True
    
    
    # resort subtaxa
    sortedSubtaxa = sorted(taxonInfo["subtaxa"], key=subtaxonSortKey)

    # (popularity of self and ancestors, then num pop ancestors, then alphabetic)
    ## Also, update sort at end of processing step below
    if "subtaxa" not in taxonInfo or taxonInfo["subtaxa"] != sortedSubtaxa:
        print("**Updating subtaxa for " + taxonName + " ( was "+str(taxonInfo["subtaxa"])+ " now " + str(sortedSubtaxa) + ")")
        taxonInfo["subtaxa"] = sortedSubtaxa
        print("--- adding to processing list '" + taxonName.lower() + "' since subtaxa updated 2")
        taxaForProcessing[taxonName.lower()] = True
        taxaForSaving[taxonName.lower()] = True


    # We are done processing this taxon, mark as complete
    if("needs_to_be_processed" in taxonInfo):
        del taxonInfo["needs_to_be_processed"]
        taxaForSaving[taxonName.lower()] = True
    if(taxonName in taxaForProcessing):
        del taxaForProcessing[taxonName]
    


######################################################3
# Output all files
for taxonName in taxaForSaving.keys():
    print("saving " + taxonName)
    taxonInfoString = json.dumps(taxaInfo[taxonName.lower()], separators=(',', ':'), indent=0, ensure_ascii=False)
    f = open("docs/taxa_processed/" + taxonName.lower() + ".json", "w", encoding="utf-8")
    f.write(taxonInfoString)
    f.close()



# Output taxon_search_list.csv

# make list of taxons
# make sure example names set to blank or json strings
taxonList = []
for taxonName in taxaInfo:
    taxonInfo = taxaInfo[taxonName]
    if not taxonInfo['otherNames'] or len(taxonInfo['otherNames']) == 0:
        taxonInfo['otherNames'] = ''
    else:
        taxonInfo['otherNames'] = json.dumps(taxonInfo['otherNames'])

    taxonList.append(taxonInfo)


with open('docs/taxon_search_list.csv', 'w',  newline='\n', encoding="utf-8") as taxon_search_list_file:
   
    fieldnames = ['name', 'otherNames', 'scientificName', 'popularity']
    
    writer = csv.DictWriter(taxon_search_list_file, fieldnames=fieldnames, extrasaction='ignore')

    writer.writeheader()

    writer.writerows(taxonList)


print("-------------------------")
print("finished processing taxa")
print("-------------------------")
# TODO: update taxon_list.json and taxon_parent_summary.json
# Note: Taxon search could use a csv that has taxon name, other names, scientific name, and popularity
