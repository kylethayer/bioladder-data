import json, os, requests, time
# you need to install requests ("pip install requests")


# Do several audits, looking for:
# - Missing parent Taxa (except Life)
# - broken wikipedia images


# Load all source taxa
taxaInfo = {}

taxaFiles = os.listdir("docs/taxa_processed")

counter = 0
for taxonFile in taxaFiles:
    if(counter % 1000 == 0):
        print("loading for processing" + taxonFile)
    counter += 1
    
    f = open("docs/taxa_processed/" + taxonFile, encoding="utf-8")
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

## Mark all taxon as needing to be have their images checked

# taxaProcessedFiles = os.listdir("docs/taxa_processed")

# taxaInfo = {}
# counter = 0


# counter = 0
# for taxonProcessedFile in taxaProcessedFiles:
    
#     if(counter % 1000 == 0):
#         print("copying over info for taxon " + taxonProcessedFile)
#     counter += 1

#     f = open("docs/taxa_processed/" + taxonProcessedFile, encoding="utf-8")
#     taxonProcessedInfo = json.loads(f.read())

#     taxonProcessedInfo["needs_wiki_img_checked"] = True

#     with open("docs/taxa_processed/" + taxonProcessedFile, 'w', encoding="utf-8") as f:
#         json.dump(taxonProcessedInfo, f, separators=(',', ':'), indent=0, ensure_ascii=False)



## check all marked taxa for their wiki images

counter = 0
taxaNameList = list(taxaInfo.keys())
print("taxaNameList" + str(taxaNameList))
taxaNameList.reverse()
# Find all subtaxa
for taxonName in taxaNameList:
    if(counter % 100 == 0):
        print("checking image file for " + taxonName)
    counter += 1

    taxonInfo = taxaInfo[taxonName.lower()]
    wikiImage = taxonInfo["wikipediaImg"]
    if(wikiImage):
        if "needs_wiki_img_checked" in taxonInfo:
            imgSucceeded = True
            try:
                r = requests.get(wikiImage, timeout = 5)
                
                if(r.status_code > 200):
                   # time.sleep(60) # retry one after one second
                   # r = requests.get(wikiImage, timeout = 5)
                   # if(r.status_code > 200):
                    print("*** Error loading '" + taxonName + "' (" + str(r.status_code) + ")")
                    print("   - url: "+ wikiImage)
                    imgSucceeded = False
                    if(r.status_code == 403):
                        time.sleep(1)
                    else:
                        print("#########################################")
                        print("#########################################")
                        print("#########################################")
                        print("marking taxon " + taxonName + " as having broken image ")
                        del taxonInfo["needs_wiki_img_checked"]
                        taxonInfo["wiki_broken_img_checked"] = True

                        with open("docs/taxa_processed/" + taxonName.lower() + ".json", 'w', encoding="utf-8") as f:
                            json.dump(taxonInfo, f, separators=(',', ':'), indent=0, ensure_ascii=False)
                time.sleep(2) # 500 requests per hour (7.5 is 480 per hour)
                
            except requests.exceptions.RequestException as e:
                print("error loading image for " + taxonName)
                print (e)
                imgSucceeded = False
            if imgSucceeded:
                # No wiki image, mark as done
                if("needs_wiki_img_checked" in taxonInfo):
                    print("marking taxon " + taxonName + " as complete (image succeeded)")
                    del taxonInfo["needs_wiki_img_checked"]

                    with open("docs/taxa_processed/" + taxonName.lower() + ".json", 'w', encoding="utf-8") as f:
                        json.dump(taxonInfo, f, separators=(',', ':'), indent=0, ensure_ascii=False)
    else:
        # No wiki image, mark as done
        if("needs_wiki_img_checked" in taxonInfo):
            print("marking taxon " + taxonName + " as complete (no image)")
            del taxonInfo["needs_wiki_img_checked"]

            with open("docs/taxa_processed/" + taxonName.lower() + ".json", 'w', encoding="utf-8") as f:
                json.dump(taxonInfo, f, separators=(',', ':'), indent=0, ensure_ascii=False)
