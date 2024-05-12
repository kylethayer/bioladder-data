let currentTaxon


function isTaxonNameValid(taxonName){
    return /^[-_\w\s'ñ]+$/.test(taxonName)
}

function init(){
    showTaxonEditingView()


    document.getElementById("new_taxon_name").onchange = UpdateTaxonName
    document.getElementById("new_taxon_name").onclick = UpdateTaxonName
    document.getElementById("new_taxon_name").onkeydown = UpdateTaxonName
    document.getElementById("new_taxon_name").onkeyup = UpdateTaxonName

    document.getElementById("subtaxon_name_input").onchange = UpdateCreateSubTaxonName
    document.getElementById("subtaxon_name_input").onclick = UpdateCreateSubTaxonName
    document.getElementById("subtaxon_name_input").onkeydown = UpdateCreateSubTaxonName
    document.getElementById("subtaxon_name_input").onkeyup = UpdateCreateSubTaxonName
}

const socketUrl = "ws://"+ location.host +"/terminal"
let webSocket = new WebSocket(socketUrl)

webSocket.onmessage = (event) => {
    console.log("socket message received", event)
    const msg = JSON.parse(event.data)
    if(msg.type == "success"){
        document.getElementById("processOutput").innerText = 
            "Successfully connected to server"
    } else if(msg.type == "cl"){
        outputDiv = document.getElementById("processOutput")
        outputDiv.innerText += msg.line
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }
    
}

function processTaxa(){
    document.getElementById("processOutput").innerText = ""
    fetch("/processTaxa", {
        method: "POST"
    })
}

function auditTaxa(){
    document.getElementById("processOutput").innerText = ""
    fetch("/auditTaxa", {
        method: "POST"
    })
}


window.onhashchange = function () {
    showTaxonEditingView()
}

function UpdateTaxonName(){
    document.getElementById("gotoOrNewTaxon").href="#" + document.getElementById("new_taxon_name").value
    document.getElementById("newTaxonNameSpan").innerText = document.getElementById("new_taxon_name").value
}

function UpdateCreateSubTaxonName(){
    document.getElementById("create_subtaxon_link").href= "?parentTaxon="+ currentTaxon + "#" + document.getElementById("subtaxon_name_input").value 
    document.getElementById("create_subtaxon_name").innerText = document.getElementById("subtaxon_name_input").value
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
    'Loaded "' + taxonName + '" for editing'

    document.getElementById("name_input").value=resultJSON.name
    document.getElementById("parentTaxon_input").value=resultJSON.parentTaxon
    document.getElementById("parentTaxon_link").setAttribute("href", "#"+ resultJSON.parentTaxon)
    document.getElementById("parentTaxon_link").innerText = resultJSON.parentTaxon
    document.getElementById("description_input").value=resultJSON.description
    document.getElementById("taxonomicRank_input").value=resultJSON.taxonomicRank
    document.getElementById("taxonomicRank_rawval").innerText=resultJSON.taxonomicRank
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

    document.getElementById("name_input").value=taxonName.toLowerCase().charAt(0).toUpperCase() + taxonName.toLowerCase().slice(1)
    document.getElementById("parentTaxon_input").value= (new URLSearchParams(window.location.search)).get("parentTaxon")? (new URLSearchParams(window.location.search)).get("parentTaxon") : null
    document.getElementById("parentTaxon_link").setAttribute("href", null)
    document.getElementById("parentTaxon_link").innerText = null
    document.getElementById("description_input").value=null
    document.getElementById("taxonomicRank_input").value=""
    document.getElementById("taxonomicRank_rawval").innerText=null
    document.getElementById("scientificName_input").value=null
    document.getElementById("otherNames_input").value=null
    document.getElementById("popularity_input").value=null
    document.getElementById("extinct_input").checked=null
    document.getElementById("exampleMember_input").value=null
    document.getElementById("exampleMember_link").setAttribute("href", null)
    document.getElementById("exampleMember_link").innerText = null
    document.getElementById("exampleMemberType_input").value=""
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

function trim(possibleString){
    if(possibleString){
        return possibleString.trim()
    }else{
        return possibleString
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
        description: trim(document.getElementById("description_input").value),
        popularity: document.getElementById("popularity_input").valueAsNumber,
        extinct: document.getElementById("extinct_input").checked,
        name: trim(document.getElementById("name_input").value),
        parentTaxon: trim(document.getElementById("parentTaxon_input").value.toLowerCase()),
        exampleMember: trim(document.getElementById("exampleMember_input").value.toLowerCase()),
        exampleMemberType: exampleMemberType,
        taxonomicRank: taxonomicRank,
        scientificName: trim(document.getElementById("scientificName_input").value),
        otherNames: document.getElementById("otherNames_input").value ? document.getElementById("otherNames_input").value.split(",") : [],
        wikipediaImg: trim(document.getElementById("wikipediaImg_input").value),
        wikipediaPage: trim(document.getElementById("wikipediaPage_input").value)
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

    if(currentTaxon.toLowerCase() == taxonName.toLowerCase()){
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

function togglePopularity(){
    popExpEl = document.getElementById("popularity-explanation")
    if(popExpEl.getAttribute("hidden")){
        popExpEl.removeAttribute("hidden")
    }else {
        popExpEl.setAttribute("hidden", true)
    }
}

function toggleWikiImg(){
    wikiImgExpEl = document.getElementById("wikipediaImg-explanation")
    if(wikiImgExpEl.getAttribute("hidden")){
        wikiImgExpEl.removeAttribute("hidden")
    }else {
        wikiImgExpEl.setAttribute("hidden", true)
    }
}


