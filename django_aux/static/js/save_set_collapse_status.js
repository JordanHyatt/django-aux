// The purose of this script is to record the class names of each collapsable divs after they are clicked
// and store it in sessionStorage
function savecollapsestatus(element) {
    var key = window.location.pathname + '_collapse_states' // build the key from the window path name
    var dict = window.sessionStorage.getItem(key) // pull the existing dict from sessionStorage 
    // if that dict did not exist create it, otherwise JSON parse it
    if (dict == null) {
        dict = {}
    } else {
        dict = JSON.parse(dict)
    }
    //  Work out the new classname 
    var prevclassname = element.className
    if (prevclassname.includes('show')) {
        newclassname = prevclassname.replace(' show', '')
    } else {
        newclassname = prevclassname + ' show'
    }
    dict[element.id] = newclassname // Store the new class name in the dict
    window.sessionStorage.setItem(key, JSON.stringify(dict)) // Set the new dict in session storage using the key built previously
}

// The purose of this script is to resotore the state of collapasable divs upon document loading 
function setdivclass() {
    var key = window.location.pathname + '_collapse_states' // build the key from the path
    var dict = window.sessionStorage.getItem(key) // pull the existing dict from sessionStorage 
    // if that dict did not exist create it, otherwise JSON parse it
    if (dict == null) {
        dict = {}
    } else {
        dict = JSON.parse(dict)
    }
    // loop the sub-dictionaries setting the classnames (show or no show)
    for (var id in dict) {
        var classname = dict[id];
        document.getElementById(id).className = classname
    }
}
$(document).ready(setdivclass)
