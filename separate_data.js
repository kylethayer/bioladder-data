import {promises as fs} from 'fs'

let all_taxon = JSON.parse(await fs.readFile("all_taxon_data.json"))

let taxon_parent_summary = {}
let taxon_list = []

Object.keys(all_taxon).forEach(taxon_name => {
    let taxon_info = all_taxon[taxon_name]
    
    // add name
    let capitalizedTaxonName = taxon_name[0].toUpperCase() + taxon_name.slice(1)
    taxon_info.name = capitalizedTaxonName
    
    let taxon_file_name = taxon_name + ".json"

    // fix underscore fields
    taxon_info.parentTaxon = taxon_info.parent_taxon
    delete taxon_info.parent_taxon

    taxon_info.popularSubtaxa = taxon_info.popular_subtaxa
    delete taxon_info.popular_subtaxa

    taxon_info.exampleMember = taxon_info.example_member
    delete taxon_info.example_member

    taxon_info.exampleMemberType = taxon_info.example_member_type
    delete taxon_info.example_member_type

    taxon_info.taxonomicRank = taxon_info.taxonomic_rank
    delete taxon_info.taxonomic_rank

    taxon_info.scientificName = taxon_info.scientific_name
    delete taxon_info.scientific_name

    taxon_info.otherNames = taxon_info.other_names
    delete taxon_info.other_names

    taxon_info.wikipediaImg = taxon_info.wikipedia_img
    delete taxon_info.wikipedia_img

    taxon_info.wikipediaPage = taxon_info.wikipedia_page
    delete taxon_info.wikipedia_page
    
    taxon_info.popularAncestors = taxon_info.popular_ancestors
    delete taxon_info.popular_ancestors

    //console.log(taxon_name, taxon_info)
    fs.writeFile("taxa_processed/" + taxon_file_name, JSON.stringify(taxon_info))

    taxon_parent_summary[capitalizedTaxonName] = taxon_info["parentTaxon"]
    taxon_list.push(capitalizedTaxonName)
})

fs.writeFile("taxon_parent_summary.json", JSON.stringify(taxon_parent_summary))
fs.writeFile("taxon_list.json", JSON.stringify(taxon_list))

