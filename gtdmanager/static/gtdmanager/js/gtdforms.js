function uri2json(uri) {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); };
    uriParams = {};
    while (match = search.exec(uri))
       uriParams[decode(match[1])] = decode(match[2]);
    return uriParams;
}

function update_callback(data) {
    if (data.success) {
		$('#itemModal').modal('hide');
	} else {
		data.success = true;
		display_form(data);
	}
}

function submit() {
    data = $('form').serialize(true);
	data += '&item_id=' + 49;
	Dajaxice.gtdmanager.item_update(update_callback, uri2json(data))
	return false;
}

function display_form(data) {
    if (data.success) {
		var formDiv = $('#itemModalContent')[0];
		formDiv.innerHTML = data.form_html;
		var form = formDiv.firstChild.nextSibling
		form.onsubmit = submit;
		$('#itemModal').modal('show');
	} else {
		console.log("AJAX request failed", data)
	}
}
