
require 'rubygems'
require 'media_wiki'
require 'yaml'
#see https://github.com/jpatokal/mediawiki-gateway
#https://github.com/jpatokal/mediawiki-gateway/blob/master/lib/media_wiki/gateway.rb
#https://www.mediawiki.org/wiki/API:Edit

maxEntriesToProcess = 25
WeightAgainstBranchFraction = 0.7
AncestorPopWeight = 0.85

credentials = YAML.load_file('LoginCredentials.yaml')
$mw = MediaWiki::Gateway.new(credentials['URL']) #, options={loglevel: Logger::DEBUG})
$mw.login(credentials['UserName'], credentials['Password'])

def $mw.bot_edit(title, content, options={})
  form_data = {'action' => 'edit', 'title' => title, 'text' => content, 'summary' => (options[:summary] || ""), 'token' => get_token('edit', title)}
  form_data['minor'] = true
  form_data['bot'] = true
  form_data['section'] = options[:section].to_s if options[:section]
  make_api_request(form_data)
end

def processPopularAncestorsForTaxon(taxonEntry)
  taxonName = getEntryName(taxonEntry)
  puts ""
  puts "processPopularAncestorsForTaxon #{taxonName}..."
  parentTaxonField = getEntryField(taxonEntry, "Has Parent Taxon").first
  ancestor = []
  ancestor[0] = ""
  ancestor[1] = ""
  ancestor[2] = ""
  ancestor[3] = ""
  
  ancestorPop = []
  ancestorPop[0] = 0
  ancestorPop[1] = 0
  ancestorPop[2] = 0
  ancestorPop[3] = 0
  if(parentTaxonField)
    #now mark the parentTaxon as needing to be updated
    parentTaxonName = getEntryName(parentTaxonField)
    
    queryResults = $mw.semantic_query("[[#{parentTaxonName}]]", ['?Has Popularity', '?Has Popular Ancestor 1', 
                   '?Has Popular Ancestor 2', '?Has Popular Ancestor 3', '?Has Popular Ancestor 4'])
    parentTaxonEntry = queryResults.elements["query"].elements["results"].to_a.first
    
    ancestor[0] = getEntryName(getEntryField(parentTaxonEntry, "Has Popular Ancestor 1").first)
    ancestor[1] = getEntryName(getEntryField(parentTaxonEntry, "Has Popular Ancestor 2").first)
    ancestor[2] = getEntryName(getEntryField(parentTaxonEntry, "Has Popular Ancestor 3").first)
    ancestor[3] = getEntryName(getEntryField(parentTaxonEntry, "Has Popular Ancestor 4").first)
    
    ancestor.each_with_index do |pAncestorName, index|
      if(pAncestorName.to_s != "")
        queryResults = $mw.semantic_query("[[#{pAncestorName}]]", ['?Has Popularity'])
        ancestorResult = queryResults.elements["query"].elements["results"].first
        if(getEntryFieldValue(ancestorResult, "Has Popularity"))
          ancestorPopPopularity = getEntryFieldValue(ancestorResult, "Has Popularity").to_f
          ancestorPop[index] = ancestorPopPopularity
        end
      end
    end

    parentPopularity = getEntryFieldValue(parentTaxonEntry, "Has Popularity").to_f
    
    #Now see if it deserves a spot on the list
    #Using pAncestor, pAncestorPop, parentTaxonName, parentPopularity
    if(  parentPopularity > ancestorPop[0] * (AncestorPopWeight ** 3) ||
	     parentPopularity > ancestorPop[1] * (AncestorPopWeight ** 2) ||
         parentPopularity > ancestorPop[2] * (AncestorPopWeight ** 1) ||	   
	     parentPopularity > ancestorPop[3] || ancestor[3] == "")
      #We now will put parent in the ancestor[0] spot. 
      #See if Ancestor[0] should go into Ancestor[1] (each level works similarly)
      if(  ancestorPop[0] > ancestorPop[1] * (AncestorPopWeight ** 2) ||
	       ancestorPop[0] > ancestorPop[2] * (AncestorPopWeight ** 1) ||
	       ancestorPop[0] > ancestorPop[3] || ancestor[3] == "")
		  
        if(  ancestorPop[1] > ancestorPop[2] * (AncestorPopWeight ** 1) ||
		     ancestorPop[1] > ancestorPop[3] || ancestor[3] == "")
			
          if(ancestorPop[2] > ancestorPop[3] || ancestor[3] == "")
            ancestor[3] = ancestor[2]
            ancestorPop[3] = ancestorPop[2]
          end
          ancestor[2] = ancestor[1]
          ancestorPop[2] = ancestorPop[1]
        end
          ancestor[1] = ancestor[0]
          ancestorPop[1] = ancestorPop[0]
      end
      ancestor[0] = parentTaxonName
      ancestorPop[0] = parentPopularity
    end
  end
  
  #compare the new list to the current list, update if needed
  currentTaxonText = $mw.get(taxonName)
  anyChanges = false
  
  ancestor.each_with_index do |pAncestorName, index|
    newVal= "#{ancestor[index]}]](#{ancestorPop[index]})"
	puts "#{ancestor[index]}: #{ancestorPop[index]}"
    
    regexString = "\\|Popular Ancestor #{index+1}=([^\\n^\\r^\\|^}]*)"
    currentValMatch = (Regexp.new regexString).match(currentTaxonText)
    if(currentValMatch)
      if(newVal != currentValMatch[1])
        anyChanges = true
        currentTaxonText.sub!((Regexp.new regexString), "|Popular Ancestor #{index+1}=" + newVal)
      end
    else
	  anyChanges = true
	  currentTaxonText.sub!(/\{\{Taxon/, "{{Taxon\n|Popular Ancestor #{index+1}=" + newVal)
	end
  end

  if(anyChanges)
    currentTaxonText = markChildrenNeedUpdateInText(currentTaxonText)
  end
  
  #mark self as done
  currentTaxonText = markSelfUpdatedInText(currentTaxonText)
 
  puts ""
  puts "saving #{taxonName}... (Popular Ancestors)"
  puts currentTaxonText
  puts ""
  $mw.bot_edit(taxonName, currentTaxonText, {})
end

def processPopularSubtaxaForTaxon(taxonName)
  puts "processPopularSubtaxaForTaxon #{taxonName}..."
  queryResults = $mw.semantic_query("[[Has Parent Taxon::#{taxonName}]]", ['?Has Popular Subtaxa', '?Has Popularity'])
  descendants = queryResults.elements["query"].elements["results"].to_a
  #For each of the results gather the popular descendants and such
  
  newPopularSubtaxaString = findPopularSubtaxaString(descendants)
  
  currentTaxonText = $mw.get(taxonName)
  
  currentPopularSubtaxaMatch = /\|Popular Subtaxa=([^\n^\r^\|^}]*)/.match(currentTaxonText)
  if(currentPopularSubtaxaMatch)
    if(newPopularSubtaxaString == currentPopularSubtaxaMatch[1])
      currentTaxonText = markSelfUpdatedInText(currentTaxonText)
      $mw.bot_edit(taxonName, currentTaxonText, {})
      return #No change needed
    end
  end

  #Update this Taxon with the new popular entries
  if(currentPopularSubtaxaMatch)
    puts "updating PopularSubtaxa #{newPopularSubtaxaString}"
    currentTaxonText.sub!(/\|Popular Subtaxa=[^\n^\r^\|^}]*/, '|Popular Subtaxa=' + newPopularSubtaxaString)
  else
    puts "adding PopularSubtaxa #{newPopularSubtaxaString}"
    currentTaxonText.sub!(/\{\{Taxon/, "{{Taxon\n|Popular Subtaxa=" +newPopularSubtaxaString)
  end
    
  currentTaxonText = markAsParentOutOfDateInText(currentTaxonText)
  
  puts ""
  puts "saving #{taxonName}... (Popular Subtaxa)"
  puts currentTaxonText
  puts ""
  $mw.bot_edit(taxonName, currentTaxonText, {})
end

def findPopularSubtaxaString(descendants)
  popularityEntries = []
  descendants.each do |descendant|
    descendantName = getEntryName(descendant)
    if(getEntryFieldValue(descendant, "Has Popularity"))
        descendantPopularity = getEntryFieldValue(descendant, "Has Popularity").to_f

        puts "#{descendantName}:#{descendantPopularity}"
        popularityEntries.push({
          :name => descendantName,
          :popularity => descendantPopularity,
          :orignal_popularity => descendantPopularity,
          :branch => descendantName
        })
    end
    
    #Get PopularSubtaxa w/ popularity and add to hash under current branch
    subPopularSubtaxa = getEntryField(descendant, "Has Popular Subtaxa").to_a
    subPopularSubtaxa.each do |subDescendant|
      subDescendantName = getEntryName(subDescendant)
      subQueryResults = $mw.semantic_query("[[#{subDescendantName}]]", ['?Has Popularity'])
      subDescendantResult = subQueryResults.elements["query"].elements["results"].first
      if(getEntryFieldValue(subDescendantResult, "Has Popularity"))
        subDescendantPopularity = getEntryFieldValue(subDescendantResult, "Has Popularity").to_f
        
        puts "#{subDescendantName}:#{subDescendantPopularity}"
        popularityEntries.push({
          :name => subDescendantName,
          :popularity => subDescendantPopularity,
          :orignal_popularity => subDescendantPopularity,
          :branch => descendantName
        })
      end
    end
  end
  

  newPopularSubtaxa = []
  
  (1..3).each do |i|
    #get most popular entry
    popularityEntries = popularityEntries.sort_by{|a| [a[:popularity], a[:name]]}
    newPopular = popularityEntries.last
    if(newPopular)
      newPopularSubtaxa.push({:name => newPopular[:name], :popularity => newPopular[:orignal_popularity]})
    end
    popularityEntries.delete(newPopular)
  
    # weigh against the remaining in that same branch
    popularityEntries.each do |popularityHash|
      if(popularityHash[:branch] == newPopular[:branch])
        popularityHash[:popularity] = popularityHash[:popularity] * WeightAgainstBranchFraction
      end
    end
  end
  
  newPopularSubtaxaString = newPopularSubtaxa.map{|pd| "#{pd[:name]}]](#{pd[:popularity]})"}.join(",")
  return newPopularSubtaxaString
end

def markSelfUpdatedInText(taxonText)
  taxonText = taxonText.sub(/\|Popular Subtaxa Out Of Date=self and /, '|Popular Subtaxa Out Of Date=')
  taxonText = taxonText.sub(/\|Popular Subtaxa Out Of Date=self/, '|Popular Subtaxa Out Of Date=')
  return taxonText
end

def markChildrenNeedUpdateInText(currentTaxonText)
  currentOutOfDateMatch = /\|Popular Subtaxa Out Of Date=([^\n^\r^\|^}]*)/.match(currentTaxonText)
  if(currentOutOfDateMatch)
    if(!currentOutOfDateMatch[1].include?("children"))
      newValue = "children"
      if(currentOutOfDateMatch[1] == "self")
        newValue = "self and children"
      elsif (currentOutOfDateMatch[1] == "parent")
        newValue = "parent and children"
      elsif (currentOutOfDateMatch[1] == "self and parent")
        newValue = "self and parent and children"
      end
      return currentTaxonText.sub(/\|Popular Subtaxa Out Of Date[^\n^\r^\|^}]*/, '|Popular Subtaxa Out Of Date='+newValue)
    end
  else
    return currentTaxonText.sub(/\{\{Taxon/, "{{Taxon\n|Popular Subtaxa Out Of Date=parent")
  end
  return currentTaxonText
end

def markAsParentOutOfDateInText(currentTaxonText)
  currentOutOfDateMatch = /\|Popular Subtaxa Out Of Date=([^\n^\r^\|^}]*)/.match(currentTaxonText)
  if(currentOutOfDateMatch)
    if(!currentOutOfDateMatch[1].include?("parent"))
      newValue = "parent"
      if(currentOutOfDateMatch[1] == "self")
        newValue = "self and parent"
      elsif (currentOutOfDateMatch[1] == "children")
        newValue = "parent and children"
      elsif (currentOutOfDateMatch[1] == "self and children")
        newValue = "self and parent and children"
      end
      return currentTaxonText.sub(/\|Popular Subtaxa Out Of Date[^\n^\r^\|^}]*/, '|Popular Subtaxa Out Of Date='+newValue)
    end
  else
    return currentTaxonText.sub(/\{\{Taxon/, "{{Taxon\n|Popular Subtaxa Out Of Date=parent")
  end
  return currentTaxonText
end

def markTaxonAsSelfOutOfDate(taxonName)
  currentTaxonText = $mw.get(taxonName)
  currentOutOfDateMatch = /\|Popular Subtaxa Out Of Date=([^\n^\r^\|^}]*)/.match(currentTaxonText)
  if(currentOutOfDateMatch)
    if(currentOutOfDateMatch[1].include?("self"))
      return #Already marked
    end
    if(currentOutOfDateMatch[1] == "")
      currentTaxonText.sub!(/\|Popular Subtaxa Out Of Date[^\n^\r^\|^}]*/, '|Popular Subtaxa Out Of Date=self')
    else
      currentTaxonText.sub!(/\|Popular Subtaxa Out Of Date[^\n^\r^\|^}]*/, '|Popular Subtaxa Out Of Date=self and '+currentOutOfDateMatch[1])
    end
  else
    currentTaxonText.sub!(/\{\{Taxon/, "{{Taxon\n|Popular Subtaxa Out Of Date=self")
  end
  
  puts "Marking #{taxonName} as out of date"
  $mw.bot_edit(taxonName, currentTaxonText, {})
end

def processTaxon(entry)
  entryName = getEntryName(entry)
  outOfDate = getEntryFieldValue(entry, "Are Popular Subtaxa Out Of Date")

  if(outOfDate.include?('self'))
    processPopularSubtaxaForTaxon(entryName)
    processPopularAncestorsForTaxon(entry)
  end

  queryResults = $mw.semantic_query("[[#{entryName}]]", ['?Are Popular Subtaxa Out Of Date', '?Has Parent Taxon'])
  entry = queryResults.elements["query"].elements["results"].first
  outOfDate = getEntryFieldValue(entry, "Are Popular Subtaxa Out Of Date")
  if(outOfDate.to_s.include?('parent'))
    parentTaxon = getEntryField(entry, "Has Parent Taxon").first
    if(parentTaxon)
      #now mark the parentTaxon as needing to be updated
      markTaxonAsSelfOutOfDate(getEntryName(parentTaxon))
    end
  end
  
  queryResults = $mw.semantic_query("[[#{entryName}]]", ['?Are Popular Subtaxa Out Of Date'])
  entry = queryResults.elements["query"].elements["results"].first
  outOfDate = getEntryFieldValue(entry, "Are Popular Subtaxa Out Of Date")
  if(outOfDate.to_s.include?('children'))
    queryResults = $mw.semantic_query("[[Has Parent Taxon::#{entryName}]]", ['?Has Popular Subtaxa', '?Has Popularity'])
    descendants = queryResults.elements["query"].elements["results"].to_a
    #now mark the children taxons as needing to be updated
    descendants.each do |descendant|
      markTaxonAsSelfOutOfDate(getEntryName(descendant))
    end
  end
  
  pageText = $mw.get(entryName)
    
  pageText.sub!(/\|Popular Subtaxa Out Of Date[^\n^\r^\|^}]*/, '')
  
  puts ""
  puts "saving #{entryName}... (mark as everything updated)"
  #puts pageText
  puts ""
  $mw.bot_edit(entryName, pageText, {})
  return true
end

  
def getNextOutOfDateTaxon
  queryResults = $mw.semantic_query(
    '[[Are Popular Subtaxa Out Of Date::+]]', 
    ['?Are Popular Subtaxa Out Of Date','?Has Parent Taxon', '?Popular Subtaxa', '?Has Popularity', '?Has Popular Ancestor 1', 
                   '?Has Popular Ancestor 2', '?Has Popular Ancestor 3', '?Has Popular Ancestor 4', 'limit=1']
  )
  return queryResults.elements["query"].elements["results"].first
end

def getEntryName(entry)
    if(entry.nil?)
      return ""
    end
    return entry.attribute("fulltext").value
end

def getEntryField(entry, fieldName)
    entry.elements["printouts"].each do |a|
        if(a.attribute('label').to_s == fieldName)
            return a
        end
    end
    return nil
end

def getEntryFieldValue(entry, fieldName)
    entryField = getEntryField(entry, fieldName)
    if(entryField && entryField.first)
        return entryField.first.first.to_s
    end
    return nil
end

(1..maxEntriesToProcess).each do |i|
  entry = getNextOutOfDateTaxon()
  if(entry)
    puts "#{i}, #{getEntryName(entry)}"
    processTaxon(entry)
  else
    break
  end
  sleep(1) # pause to allow other non-bot requests to go through
end
