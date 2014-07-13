/**
 *  Converts gtdmanager URL to apropriate Dajaxice call
 *  e.g. http://localhost:8000/gtdmanager/context/create to
 *      function Dajaxice.gtdmanager.context_create
 */
function get_dajaxice_method_url(action) {
	// cmd results e.g. in gtdmanager/context/create
	var safe = action.replace(/\/<.*>|\/\d+/g, "")
	var cmd = safe.substr(safe.indexOf("gtdmanager"));
	var cmdArr = cmd.split('/')
	return window["Dajaxice"][cmdArr[0]][cmdArr[1]+"_"+cmdArr[2]];
}

function get_dajaxice_method(model, action) {
	var url = Django.url("gtdmanager:" + model + "_" + action);
	return get_dajaxice_method_url(url);
}