let currentTaxon


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
    currentTaxon = taxonName
    let response = await fetch("getTaxon?taxonName="+taxonName)
    let resultJSON = await response.json();

    if(currentTaxon != taxonName){
        return
    }



    if(resultJSON.error){
        document.getElementById("view_edit_taxon_message").innerText = 
        "Response: "+ JSON.stringify(resultJSON)
        if(resultJSON.error.includes("No such file")){
            clearAndDisplayEditor(taxonName)
        }
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
    document.getElementById("taxonomicRank_rawval").value=resultJSON.taxonomicRank
    document.getElementById("scientificName_input").value=resultJSON.scientificName
    document.getElementById("otherNames_input").value=resultJSON.otherNames
    document.getElementById("popularity_input").value=resultJSON.popularity
    document.getElementById("extinct_input").checked=resultJSON.extinct
    document.getElementById("exampleMember_input").value=resultJSON.exampleMember
    document.getElementById("exampleMember_link").setAttribute("href", "#"+ resultJSON.exampleMember)
    document.getElementById("exampleMember_link").innerText = resultJSON.exampleMember
    document.getElementById("exampleMemberType_input").value=resultJSON.exampleMemberType
    document.getElementById("exampleMemberType_rawval").innerText=resultJSON.exampleMemberType
    document.getElementById("wikipediaImg_input").value=resultJSON.wikipediaImg
    document.getElementById("wikipediaImg_preview").src=resultJSON.wikipediaImg
    document.getElementById("wikipediaPage_input").value=resultJSON.wikipediaPage
    document.getElementById("wikipediaPage_link").href=resultJSON.wikipediaPage
    document.getElementById("wikipediaPage_link").innerText=resultJSON.wikipediaPage

    document.getElementById("subtaxa").innerHTML = ""
    document.getElementById("popularSubtaxa").innerHTML = ""
    document.getElementById("popularAncestors").innerHTML = ""


    document.getElementById("view_edit_taxon_box").removeAttribute("hidden")
    loadTaxonProcessedFields(taxonName)
}

function clearAndDisplayEditor(taxonName){
    document.getElementById("view_edit_taxon_message").innerText = 
    "Creating new taxon: " + taxonName 

    document.getElementById("name_input").value=null
    document.getElementById("parentTaxon_input").value=null
    document.getElementById("parentTaxon_link").setAttribute("href", null)
    document.getElementById("parentTaxon_link").innerText = null
    document.getElementById("description_input").value=null
    document.getElementById("taxonomicRank_input").value=null
    document.getElementById("taxonomicRank_rawval").value=null
    document.getElementById("scientificName_input").value=null
    document.getElementById("otherNames_input").value=null
    document.getElementById("popularity_input").value=null
    document.getElementById("extinct_input").checked=null
    document.getElementById("exampleMember_input").value=null
    document.getElementById("exampleMember_link").setAttribute("href", null)
    document.getElementById("exampleMember_link").innerText = null
    document.getElementById("exampleMemberType_input").value=null
    document.getElementById("exampleMemberType_rawval").innerText=null
    document.getElementById("wikipediaImg_input").value=null
    document.getElementById("wikipediaImg_preview").src=null
    document.getElementById("wikipediaPage_input").value=null
    document.getElementById("wikipediaPage_link").href=null
    document.getElementById("wikipediaPage_link").innerText=null

    document.getElementById("subtaxa").innerHTML = ""
    document.getElementById("popularSubtaxa").innerHTML = ""
    document.getElementById("popularAncestors").innerHTML = ""


    document.getElementById("view_edit_taxon_box").removeAttribute("hidden")
}


async function loadTaxonProcessedFields(taxonName){
    let response = await fetch("getProcessedTaxon?taxonName="+taxonName)
    let resultJSON = await response.json();

    if(currentTaxon != taxonName){
        return
    }

    if(resultJSON.subtaxa){
        resultJSON.subtaxa.forEach(subtaxon => {
            let subtaxonDom = document.createElement("a")
            subtaxonDom.setAttribute("href", "#"+ subtaxon)
            subtaxonDom.innerText = subtaxon
            document.getElementById("subtaxa").append(subtaxonDom)
            document.getElementById("subtaxa").innerHTML += ", "
        })
    }

    if(resultJSON.popularSubtaxa){
        resultJSON.popularSubtaxa.forEach(subtaxon => {
            let subtaxonDom = document.createElement("a")
            subtaxonDom.setAttribute("href", "#"+ subtaxon)
            subtaxonDom.innerText = subtaxon
            document.getElementById("popularSubtaxa").append(subtaxonDom)
            document.getElementById("popularSubtaxa").innerHTML += ", "
        })
    }

    if(resultJSON.popularAncestors){
        resultJSON.popularAncestors.forEach(ancestor => {
            let ancestorDom = document.createElement("a")
            ancestorDom.setAttribute("href", "#"+ ancestor)
            ancestorDom.innerText = ancestor
            document.getElementById("popularAncestors").append(ancestorDom)
            document.getElementById("popularAncestors").innerHTML += ", "
        })
    }
}

async function saveTaxon(){
    let taxonName = document.getElementById("name_input").value

    // get values from select boxes
    taxonomicRank_input = document.getElementById("taxonomicRank_input")
    taxonomicRank = taxonomicRank_input.options[taxonomicRank_input.selectedIndex].value;
    
    exampleMemberType_input = document.getElementById("exampleMemberType_input")
    exampleMemberType = exampleMemberType_input.options[exampleMemberType_input.selectedIndex].value;
    
    let taxonJSON = {
        name: document.getElementById("name_input").value,
        parentTaxon: document.getElementById("parentTaxon_input").value.toLowerCase(),
        description: document.getElementById("description_input").value,
        taxonomicRank: taxonomicRank,
        scientificName: document.getElementById("scientificName_input").value,
        otherNames: document.getElementById("otherNames_input").value ? document.getElementById("otherNames_input").value.split(",") : [],
        popularity: document.getElementById("popularity_input").value,
        extinct: document.getElementById("extinct_input").checked,
        exampleMember: document.getElementById("exampleMember_input").value.toLowerCase(),
        exampleMemberType: exampleMemberType,
        wikipediaImg: document.getElementById("wikipediaImg_input").value,
        wikipediaPage: document.getElementById("wikipediaPage_input").value
    }

    let response = await fetch("saveTaxon", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(taxonJSON)
    })
    let responseText = await response.text()
    if(response.status >= 400 || responseText.includes("error")){
        alert(responseText)
    }

    if(currentTaxon == taxonName){
        loadTaxon(taxonName)
    }
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