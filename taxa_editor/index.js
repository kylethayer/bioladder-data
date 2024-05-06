
function isTaxonNameValid(taxonName){
    return /^[-_\w\s'ñ]+$/.test(taxonName)
}

async function init(){
    showTaxonEditingView()
}

async function showTaxonEditingView(){
    let taxon_name = window.location.hash.substring(1)
    if(!taxon_name){
        document.getElementById("view_edit_taxon").innerText = 
            "No Taxon Name Selected"
        return
    }
    if(!isTaxonNameValid(taxon_name)){
        document.getElementById("view_edit_taxon").innerText = 
            "Taxon name not valid: "+ taxon_name

        return
    }
    // TODO: Try to load source and processed version of file
    document.getElementById("view_edit_taxon").innerText = 
            "Editing: "+ taxon_name
}

function createNewTaxon(){
    let newTaxonName = document.getElementById("new_taxon_name").value
    if(!isTaxonNameValid()){
        alert("Invalid taxon name:" + newTaxonName)
    }
    window.location.hash = "#" + newTaxonName
    showTaxonEditingView()
}