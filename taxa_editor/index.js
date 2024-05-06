
function isTaxonNameValid(taxonName){
    return /^[-_\w\s'ñ]+$/.test(taxonName)
}

function init(){
    showTaxonEditingView()
}

window.onhashchange = function () {
    showTaxonEditingView()
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
        alert("Invalid taxon name:" + taxonName)
        return
    }
    let response = await fetch("getTaxon?taxonName="+taxonName)
    let resultJSON = await response.json();



    if(resultJSON.error){
        document.getElementById("view_edit_taxon_message").innerText = 
        "Response: "+ JSON.stringify(resultJSON)
        return
    }

    document.getElementById("view_edit_taxon_message").innerText = 
    "Loaded " + taxonName + " for editing"

    document.getElementById("name_input").value=resultJSON.name
    document.getElementById("parentTaxon_input").value=resultJSON.parentTaxon
    document.getElementById("parentTaxon_link").setAttribute("href", "#"+ resultJSON.parentTaxon)
    document.getElementById("parentTaxon_link").innerText = resultJSON.parentTaxon
    document.getElementById("description_input").value=resultJSON.description
    document.getElementById("taxonomicRank_input").value=resultJSON.taxonomicRank
    document.getElementById("scientificName_input").value=resultJSON.scientificName
    document.getElementById("otherNames_input").value=resultJSON.otherNames
    document.getElementById("popularity_input").value=resultJSON.popularity
    document.getElementById("extinct_input").value=resultJSON.extinct
    document.getElementById("exampleMember_input").value=resultJSON.exampleMember
    document.getElementById("exampleMember_link").setAttribute("href", "#"+ resultJSON.exampleMember)
    document.getElementById("exampleMember_link").innerText = resultJSON.exampleMember
    document.getElementById("exampleMemberType_input").value=resultJSON.exampleMemberType
    document.getElementById("wikipediaImg_input").value=resultJSON.wikipediaImg
    document.getElementById("wikipediaPage_input").value=resultJSON.wikipediaPage



    document.getElementById("view_edit_taxon_box").removeAttribute("hidden")
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