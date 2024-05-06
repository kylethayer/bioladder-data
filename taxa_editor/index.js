
function isTaxonNameValid(taxonName){
    return /^[-_\w\s'ñ]+$/.test(taxonName)
}

function init(){
    showTaxonEditingView()
    //TMP
    document.getElementById("view_edit_taxon_box").removeAttribute("hidden")
}

async function showTaxonEditingView(){
    let taxonName = window.location.hash.substring(1)
    taxonName = decodeURI(taxonName)
    if(!taxonName){
        document.getElementById("view_edit_taxon_message").innerText = 
            "No Taxon Name Selected"
        return
    }
    if(!isTaxonNameValid(taxonName)){
        document.getElementById("view_edit_taxon_message").innerText = 
            "Taxon name not valid: "+ taxonName
        return
    }

    document.getElementById("view_edit_taxon_message").innerText = 
            "Attempting to load taxon: "+ taxonName
    loadTaxon(taxonName)
}

async function loadTaxon(taxonName){
    if(!isTaxonNameValid()){
        alert("Invalid taxon name:" + newTaxonName)
        return
    }
    let response = await fetch("getTaxon?taxonName="+taxonName)
    let resultJSON = await response.json();

    document.getElementById("view_edit_taxon_message").innerText = 
    "Response: "+ JSON.stringify(resultJSON)
}

function createNewTaxon(){
    let newTaxonName = document.getElementById("new_taxon_name").value
    if(!isTaxonNameValid()){
        alert("Invalid taxon name:" + newTaxonName)
        return
    }
    window.location.hash = "#" + newTaxonName
    showTaxonEditingView()
}