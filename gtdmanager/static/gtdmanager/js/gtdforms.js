/**
 *  Class for handling forms via Dajaxice
 */

function GtdForm(caption) {
	this.caption = caption;
}

GtdForm.prototype.display_form = function (data) {
    if (data.form_html) {
		var caption = $('#itemModalLabel')[0];
		caption.textContent = this.caption;
		var formDiv = $('#itemModalContent')[0];
		formDiv.innerHTML = data.form_html;
		var form = formDiv.firstChild.nextSibling
		form.onsubmit = data.itemId ? this._submit.bind(this, data.itemId, form.action)
								    : this._submit.bind(this, null, form.action);
		$('#itemModal').modal('show');
		setTimeout(function() { $('#id_name').focus(); }, 500);
	} else {
		console.log("No HTML form data returned", data)
	}
}

GtdForm.prototype._uri2json = function (uri) {
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

GtdForm.prototype._update_callback = function(data) {
    if (data.success) {
		$('#itemModal').modal('hide');
		window.location.reload();
	} else {
		this._display_form(data);
	}
}

GtdForm.prototype._submit = function (itemId, action) {
    data = $('form').serialize(true);
	if (itemId) {
		data += '&item_id=' + itemId;
	}
	var method = get_dajaxice_method_url(action);
	method(this._update_callback.bind(this), this._uri2json(data))
	return false;
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