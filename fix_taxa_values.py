# This is meant for temporary scripts to fix something about how current information is saved
# e.g., change img http:// => https://

import json, os

# fix http:// => https:// in wikipediaImgs

taxaSourceFiles = os.listdir("docs/taxa_source")
counter = 0

for taxonSourceFile in taxaSourceFiles:
    
    if(counter % 1000 == 0):
        print("copying over info for taxon " + taxonSourceFile)
    counter += 1

    f = open("docs/taxa_source/" + taxonSourceFile, encoding="utf-8")
    taxonSourceInfo = json.loads(f.read())

    if("http://" in taxonSourceInfo["wikipediaImg"]):
        taxonSourceInfo["wikipediaImg"] = taxonSourceInfo["wikipediaImg"].replace("http://", "https://")

    with open("docs/taxa_source/" + taxonSourceFile, 'w') as f:
        json.dump(taxonSourceInfo, f, indent=0)

counter = 0
for taxonSourceFile in taxaSourceFiles:
    
    if(counter % 1000 == 0):
        print("copying over info for taxon " + taxonSourceFile)
    counter += 1

    f = open("docs/taxa_processed/" + taxonSourceFile, encoding="utf-8")
    taxonSourceInfo = json.loads(f.read())

    if("http://" in taxonSourceInfo["wikipediaImg"]):
        taxonSourceInfo["wikipediaImg"] = taxonSourceInfo["wikipediaImg"].replace("http://", "https://")

    with open("docs/taxa_processed/" + taxonSourceFile, 'w') as f:
        json.dump(taxonSourceInfo, f, indent=0)




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

#     with open("docs/taxa_source/" + taxonSourceFile, 'w') as f:
#         json.dump(taxonSourceInfo, f, indent=0)


# for taxonSourceFile in taxaSourceFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonSourceFile)
#     counter += 1

#     f = open("docs/taxa_processed/" + taxonSourceFile, encoding="utf-8")
#     taxonSourceInfo = json.loads(f.read())

#     with open("docs/taxa_processed/" + taxonSourceFile, 'w') as f:
#         json.dump(taxonSourceInfo, f, indent=0)






