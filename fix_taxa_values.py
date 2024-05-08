# This is meant for temporary scripts to fix something about how current information is saved
# e.g., change img http:// => https://

import json, os


####################################3
# Add popularSubtaxaPops

taxaProcessedFiles = os.listdir("docs/taxa_processed")

taxaInfo = {}
counter = 0

for taxonFile in taxaProcessedFiles:
    if(counter % 1000 == 0):
        print("loading for processing " + taxonFile)
    counter += 1
    
    f = open("docs/taxa_processed/" + taxonFile, encoding="utf-8")
    taxonInfo = json.loads(f.read())
    taxaInfo[taxonInfo["name"].lower()] = taxonInfo 

for taxonName in taxaInfo.keys():
    taxonInfo = taxaInfo[taxonName]
    popularSubtaxaPops = []
    if("popularSubtaxa" not in taxonInfo):
        print("could not find popularSubtaxa in " + str(taxonName))
        taxonInfo["popularSubtaxa"] = []
        taxonInfo["needs_to_be_processed"] = True
    else:
        for popSubtaxa in taxonInfo["popularSubtaxa"]:
            popularSubtaxaPops.append(taxaInfo[popSubtaxa.lower()]["popularity"])
    
    taxonInfo["popularSubtaxaPops"] = popularSubtaxaPops

    with open("docs/taxa_processed/" + taxonName.lower() + ".json", 'w', encoding="utf-8") as f:
        json.dump(taxonInfo, f, indent=0)

# ####################################3
# # Add popularAncestorPops

# taxaProcessedFiles = os.listdir("docs/taxa_processed")

# taxaInfo = {}
# counter = 0

# for taxonFile in taxaProcessedFiles:
#     if(counter % 1000 == 0):
#         print("loading for processing" + taxonFile)
#     counter += 1
    
#     f = open("docs/taxa_processed/" + taxonFile, encoding="utf-8")
#     taxonInfo = json.loads(f.read())
#     taxaInfo[taxonInfo["name"].lower()] = taxonInfo 

# for taxonName in taxaInfo.keys():
#     taxonInfo = taxaInfo[taxonName]
#     popularAncestorPops = [None, None, None, None]
#     if("popularAncestors" not in taxonInfo):
#         print("could not find popularAncestors in " + str(taxonName))
#         taxonInfo["popularAncestors"] = [None, None, None, None]
#         taxonInfo["needs_to_be_processed"] = True
#     else:
#         for i, popAncestor in enumerate(taxonInfo["popularAncestors"]):
#             if(popAncestor):
#                 if(popAncestor.lower() in taxaInfo): 
#                     popularAncestorPops[i] = taxaInfo[popAncestor.lower()]["popularity"]
#                 else: 
#                     popularAncestorPops[i] = None
#                     taxonInfo["needs_to_be_processed"] = True
#             else:
#                 popularAncestorPops[i] = None
    
#     taxonInfo["popularAncestorPops"] = popularAncestorPops

#     with open("docs/taxa_processed/" + taxonName.lower() + ".json", 'w', encoding="utf-8") as f:
#         json.dump(taxonInfo, f, indent=0)


##############################
# fix http:// => https:// in wikipediaImgs

# taxaSourceFiles = os.listdir("docs/taxa_source")
# counter = 0

# for taxonSourceFile in taxaSourceFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonSourceFile)
#     counter += 1

#     f = open("docs/taxa_source/" + taxonSourceFile, encoding="utf-8")
#     taxonSourceInfo = json.loads(f.read())

#     if("http://" in taxonSourceInfo["wikipediaImg"]):
#         taxonSourceInfo["wikipediaImg"] = taxonSourceInfo["wikipediaImg"].replace("http://", "https://")

#     with open("docs/taxa_source/" + taxonSourceFile, 'w', encoding="utf-8") as f:
#         json.dump(taxonSourceInfo, f, indent=0)

# counter = 0
# for taxonSourceFile in taxaSourceFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonSourceFile)
#     counter += 1

#     f = open("docs/taxa_processed/" + taxonSourceFile, encoding="utf-8")
#     taxonSourceInfo = json.loads(f.read())

#     if("http://" in taxonSourceInfo["wikipediaImg"]):
#         taxonSourceInfo["wikipediaImg"] = taxonSourceInfo["wikipediaImg"].replace("http://", "https://")

#     with open("docs/taxa_processed/" + taxonSourceFile, 'w', encoding="utf-8") as f:
#         json.dump(taxonSourceInfo, f, indent=0)


#######################################33
# make all json files have newlines (for checking value changes in git commits easier)
# taxaSourceFiles = os.listdir("docs/taxa_source")

# counter = 0

# for taxonSourceFile in taxaSourceFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonSourceFile)
#     counter += 1

#     f = open("docs/taxa_source/" + taxonSourceFile, encoding="utf-8")
#     taxonSourceInfo = json.loads(f.read())

#     with open("docs/taxa_source/" + taxonSourceFile, 'w', encoding="utf-8") as f:
#         json.dump(taxonSourceInfo, f, indent=0)


# for taxonSourceFile in taxaSourceFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonSourceFile)
#     counter += 1

#     f = open("docs/taxa_processed/" + taxonSourceFile, encoding="utf-8")
#     taxonSourceInfo = json.loads(f.read())

#     with open("docs/taxa_processed/" + taxonSourceFile, 'w', encoding="utf-8") as f:
#         json.dump(taxonSourceInfo, f, indent=0)






