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

function update_callback(formCaption, data) {
    if (data.success) {
		$('#itemModal').modal('hide');
		window.location.reload();
	} else {
		display_form(formCaption, data);
	}
}

function submit(formCaption, itemId) {
    data = $('form').serialize(true);
	if (itemId) {
		data += '&item_id=' + itemId;
		Dajaxice.gtdmanager.item_update(update_callback.bind(this, formCaption), uri2json(data))
	} else {
		Dajaxice.gtdmanager.item_create(update_callback.bind(this, formCaption), uri2json(data))
	}
	return false;
}

function display_form(formCaption, data) {
    if (data.form_html) {
		var caption = $('#itemModalLabel')[0];
		caption.innerText = formCaption;
		var formDiv = $('#itemModalContent')[0];
		formDiv.innerHTML = data.form_html;
		var form = formDiv.firstChild.nextSibling
		form.onsubmit = data.itemId ? submit.bind(this, formCaption, data.itemId)
								    : submit.bind(this, formCaption, null);
		$('#itemModal').modal('show');
	} else {
		console.log("No HTML form data returned", data)
	}
}
