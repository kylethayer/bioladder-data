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



#### Relevant ruby code

# maxEntriesToProcess = 25
# WeightAgainstBranchFraction = 0.7
# AncestorPopWeight = 0.85


#########################
# given parent popular ancestors and parent popularity, does parent go into the current taxon's popular ancestor list?

#     parentPopularity = getEntryFieldValue(parentTaxonEntry, "Has Popularity").to_f
    
#     #Now see if it deserves a spot on the list
#     #Using pAncestor, pAncestorPop, parentTaxonName, parentPopularity
#     if(  parentPopularity > ancestorPop[0] * (AncestorPopWeight ** 3) ||
# 	     parentPopularity > ancestorPop[1] * (AncestorPopWeight ** 2) ||
#          parentPopularity > ancestorPop[2] * (AncestorPopWeight ** 1) ||	   
# 	     parentPopularity > ancestorPop[3] || ancestor[3] == "")
#       #We now will put parent in the ancestor[0] spot. 
#       #See if Ancestor[0] should go into Ancestor[1] (each level works similarly)
#       if(  ancestorPop[0] > ancestorPop[1] * (AncestorPopWeight ** 2) ||
# 	       ancestorPop[0] > ancestorPop[2] * (AncestorPopWeight ** 1) ||
# 	       ancestorPop[0] > ancestorPop[3] || ancestor[3] == "")
		  
#         if(  ancestorPop[1] > ancestorPop[2] * (AncestorPopWeight ** 1) ||
# 		     ancestorPop[1] > ancestorPop[3] || ancestor[3] == "")
			
#           if(ancestorPop[2] > ancestorPop[3] || ancestor[3] == "")
#             ancestor[3] = ancestor[2]
#             ancestorPop[3] = ancestorPop[2]
#           end
#           ancestor[2] = ancestor[1]
#           ancestorPop[2] = ancestorPop[1]
#         end
#           ancestor[1] = ancestor[0]
#           ancestorPop[1] = ancestorPop[0]
#       end
#       ancestor[0] = parentTaxonName
#       ancestorPop[0] = parentPopularity
#     end
#   end

#   if(anyChanges)
#     currentTaxonText = markChildrenNeedUpdateInText(currentTaxonText)
#   end
  
################################################33
# Popular subtaxa

# popularityEntries = [] #options for popular subtaxa

    # Put descendants in pupularEntries (with branch, which is themselves)
#   descendants.each do |descendant| (inlcuding branch)
#     descendantName = getEntryName(descendant)
#     if(getEntryFieldValue(descendant, "Has Popularity"))
#         descendantPopularity = getEntryFieldValue(descendant, "Has Popularity").to_f

#         puts "#{descendantName}:#{descendantPopularity}"
#         popularityEntries.push({
#           :name => descendantName,
#           :popularity => descendantPopularity,
#           :orignal_popularity => descendantPopularity,
#           :branch => descendantName
#         })
#     end
    
    #Popular subtaxa of each descendant (with branch)
#     #Get PopularSubtaxa w/ popularity and add to hash under current branch
#     subPopularSubtaxa = getEntryField(descendant, "Has Popular Subtaxa").to_a
#     subPopularSubtaxa.each do |subDescendant|
#       subDescendantName = getEntryName(subDescendant)
#       subQueryResults = $mw.semantic_query("[[#{subDescendantName}]]", ['?Has Popularity'])
#       subDescendantResult = subQueryResults.elements["query"].elements["results"].first
#       if(getEntryFieldValue(subDescendantResult, "Has Popularity"))
#         subDescendantPopularity = getEntryFieldValue(subDescendantResult, "Has Popularity").to_f
        
#         puts "#{subDescendantName}:#{subDescendantPopularity}"
#         popularityEntries.push({
#           :name => subDescendantName,
#           :popularity => subDescendantPopularity,
#           :orignal_popularity => subDescendantPopularity,
#           :branch => descendantName
#         })
#       end
#     end
#   end
  

#   newPopularSubtaxa = []
  
    # Get top three, one at a time, choose one, and then weigh down popularity of entries in that
    # branch
#   (1..3).each do |i|
#     #get most popular entry
#     popularityEntries = popularityEntries.sort_by{|a| [a[:popularity], a[:name]]}
#     newPopular = popularityEntries.last
#     if(newPopular)
#       newPopularSubtaxa.push({:name => newPopular[:name], :popularity => newPopular[:orignal_popularity]})
#     end
#     popularityEntries.delete(newPopular)
  
#     # weigh against the remaining in that same branch
#     popularityEntries.each do |popularityHash|
#       if(popularityHash[:branch] == newPopular[:branch])
#         popularityHash[:popularity] = popularityHash[:popularity] * WeightAgainstBranchFraction
#       end
#     end
#   end
  
#   newPopularSubtaxaString = newPopularSubtaxa.map{|pd| "#{pd[:name]}]](#{pd[:popularity]})"}.join(",")
#   return newPopularSubtaxaString