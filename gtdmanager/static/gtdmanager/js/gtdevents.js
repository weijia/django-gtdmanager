function GtdEvents() {
    this._signals = {}
}

/* public */

GtdEvents.prototype.emit = function (signalName, data) {
    var event = new CustomEvent(signalName, data);
    document.dispatchEvent(event);
    console.log('Signal ' + signalName + ' emited');
    console.log(data);
}

GtdEvents.prototype.complete_callback = function () {
    return this._getDataCallback('gtdcomplete', "Complete failed")
}

GtdEvents.prototype.delete_callback = function () {
    return this._getDataCallback('gtddelete', "Delete failed");
}

GtdEvents.prototype.item_reference_callback = function () {
    return this._getDataCallback('gtditemref', "Converting to reference failed");
}

GtdEvents.prototype.item_someday_callback = function () {
    return this._getDataCallback('gtditemsm', "Converting to someday / maybe failed");
}

GtdEvents.prototype.item2project_callback = function () {
    return this._getDataCallback('gtditem2proj', "Converting to project failed");
}

GtdEvents.prototype.item_waitfor_callback = function () {
    return this._getDataCallback('gtditemwait', "Converting to waiting for failed");
}

/* protected */

GtdEvents.prototype._dataCallback = function(signalName, errorMsg, data) {
    if (data.success) {
        this.emit(signalName, data)
	} else {
        data['displayMessage'] = errorMsg;
        this.emit('gtderror', data);
	}
}

GtdEvents.prototype._getDataCallback = function(signalName, errorMsg) {
    return this._dataCallback.bind(this, signalName, errorMsg)
}