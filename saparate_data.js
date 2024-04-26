import {promises as fs} from 'fs'

let all_taxon = JSON.parse(await fs.readFile("all_taxon_data.json"))

Object.keys(all_taxon).forEach(taxon_name => {
    let taxon_info = all_taxon[taxon_name]
    taxon_info.name = taxon_name
    let taxon_file_name = taxon_name.replaceAll(" ", "_") + ".json"
    //console.log(taxon_name, taxon_info)
    fs.writeFile("taxa/" + taxon_file_name, JSON.stringify(taxon_info))
})

