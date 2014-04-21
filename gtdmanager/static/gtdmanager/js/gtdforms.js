function uri2json(uri) {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); };
    var uriParams = {};
    while (match = search.exec(uri)) {
		var name = decode(match[1]);
		var value = decode(match[2]);
		if (name == "contexts") {
			if (uriParams.contexts == undefined) {
				uriParams.contexts = []
			}
			uriParams.contexts.push(value)
		} else {
			uriParams[name] = value;
		}
    }
    return uriParams;
}

function get_method(create, action) {
	if (create) {
		if (action.indexOf("item/create") > -1) {
			return Dajaxice.gtdmanager.item_create;
		} else if (action.indexOf("reminder/create") > -1) {
			return Dajaxice.gtdmanager.reminder_create;
		} else if (action.indexOf("next/create") > -1) {
			return Dajaxice.gtdmanager.next_create;
		}  else if (action.indexOf("project/create") > -1) {
			return Dajaxice.gtdmanager.project_create;
		}  else if (action.indexOf("context/create") > -1) {
			return Dajaxice.gtdmanager.context_create;
		}
	} else {
		if (action.indexOf("item/update") > -1) {
			return Dajaxice.gtdmanager.item_update;
		} else if (action.indexOf("reminder/update") > -1) {
			return Dajaxice.gtdmanager.reminder_update;
		} else if (action.indexOf("next/update") > -1) {
			return Dajaxice.gtdmanager.next_update;
		} else if (action.indexOf("project/update") > -1) {
			return Dajaxice.gtdmanager.project_update;
		} else if (action.indexOf("context/update") > -1) {
			return Dajaxice.gtdmanager.context_update;
		}
	}
}

function update_callback(formCaption, data) {
    if (data.success) {
		$('#itemModal').modal('hide');
		window.location.reload();
	} else {
		display_form(formCaption, data);
	}
}

function submit(formCaption, itemId, action) {
    data = $('form').serialize(true);
	if (itemId) {
		data += '&item_id=' + itemId;
	}
	var method = get_method(itemId ? false : true, action);
	method(update_callback.bind(this, formCaption), uri2json(data))
	return false;
}

function display_form(formCaption, data) {
    if (data.form_html) {
		var caption = $('#itemModalLabel')[0];
		caption.textContent = formCaption;
		var formDiv = $('#itemModalContent')[0];
		formDiv.innerHTML = data.form_html;
		var form = formDiv.firstChild.nextSibling
		form.onsubmit = data.itemId ? submit.bind(this, formCaption, data.itemId, form.action)
								    : submit.bind(this, formCaption, null, form.action);
		$('#itemModal').modal('show');
		setTimeout(function() { $('#id_name').focus(); }, 500);
	} else {
		console.log("No HTML form data returned", data)
	}
}

function delete_callback(data) {
	if (data.success) {
		window.location.reload();
	} else {
		alert("Delete failed");
	}
}

function complete_callback(data) {
	if (data.success) {
		window.location.reload();
	} else {
		alert("Complete failed");
	}
}