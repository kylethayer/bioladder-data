import {promises as fs} from 'fs'

let all_taxon = JSON.parse(await fs.readFile("all_taxon_data.json"))

let taxon_parent_summary = {}
let taxon_list = []

Object.keys(all_taxon).forEach(taxon_name => {
    let taxon_info = all_taxon[taxon_name]
    taxon_info.name = taxon_name
    let taxon_file_name = taxon_name.replaceAll(" ", "_") + ".json"
    //console.log(taxon_name, taxon_info)
    fs.writeFile("taxa/" + taxon_file_name, JSON.stringify(taxon_info))

    taxon_parent_summary[taxon_name] = taxon_info["parent_taxon"]
    taxon_list.push(taxon_name)
})

fs.writeFile("taxon_parent_summary.json", JSON.stringify(taxon_parent_summary))
fs.writeFile("taxon_list.json", JSON.stringify(taxon_list))

