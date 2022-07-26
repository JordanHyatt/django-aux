// The purose of this script is to record the x and y scroll position for every page in the site
// into the sessionStorage
function saveScroll() {
    var key = window.location.pathname + '_yscroll' // get the path name and combine with y for a unique key
    window.sessionStorage.setItem(key, window.scrollY) // store in session variables
    var key = window.location.pathname + '_xscroll' // get the path name and combine with x for a unique key
    window.sessionStorage.setItem(key, window.scrollX) // store in session variables
}
window.onscroll = saveScroll

// The purose of this script is to retreive the x and y scroll position of a given pathname
// and scroll the window to it
function setScroll() {
    var key = window.location.pathname + '_yscroll' // Build the unique key for yscroll
    y = window.sessionStorage.getItem(key) // store in session variables
    var key = window.location.pathname + '_xscroll' // Build the unique key for xscroll
    x = window.sessionStorage.getItem(key)
    setTimeout(function () {
        window.scrollTo(x, y);
    }, 200);
}
$(document).ready(setScroll)