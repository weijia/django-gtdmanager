
/**
 *  Class for building pages in JS
 */
function GtdPages(divName) {
    this._contentDiv = $('#content');
    if (this._contentDiv.length != 1) {
        console.log("Cannot find content div");
        this.div = null;
    }
    this._factory = new GtdControlFactory()
}

GtdPages.prototype._appendList = function (divName, rows) {
    this._contentDiv.append($('<div id="'+ divName + '" class="col-xs-' + rows + '"></div>'));
    return new GtdList(divName);
}

GtdPages.prototype.displayError = function(msg, data) {
    text = msg;
    if (data.message) {
        text += ': ' + data.message;
    }
    alert(text);
}

GtdPages.prototype.context_setdefault_callback = function(data) {
    if (!data.success) {
        this.displayError('Setting default context failed', data);
        // TODO - select radio at original default context
    }
}

GtdPages.prototype.confirm_clean = function() {
    if (confirm("Do you really want to remove all items from archive (this action cannot be undone)?")) {

        var done = function (data) {
            if (data.success) {
                this.buildArchive([], [])
            } else {
                this.displayError("Archive clean failed");
            }
        }
        Dajaxice.gtdmanager.archive_clean(done.bind(this));
    }
}

GtdPages.prototype._archiveTable = function (title, divName, listData) {
    this._contentDiv.append($('<h2>' + title + '</h2>'));
    var list = this._appendList(divName, 8)
    list.buildItems(listData, [2, 3], false);
}

GtdPages.prototype.buildArchive = function(completed, deleted) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Archive</h1>'));

    if (completed.length || deleted.length) {
        btn = this._factory.getBtnCleanArchive(this.confirm_clean.bind(this));
        this._contentDiv.append(btn);
    } else {
        this._contentDiv.append($('<span>No archived item found</span>'));
    }

    if (completed.length) {
        this._archiveTable('Completed', 'list-items-completed', completed);
        this._contentDiv.append($('<div class="clearDiv" />'));
    }

    if (deleted.length) {
        this._archiveTable('Deleted', 'list-items-deleted', deleted);
    }
}

GtdPages.prototype.buildContexts = function(data) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Contexts</h1>'));
    this._contentDiv.append($('<p></p>').append(this._factory.getBtnCreateContext()));
    list = this._appendList('list-contexts', 4);
    list.buildContexts(data, this.context_setdefault_callback.bind(this));
}

GtdPages.prototype.buildInbox = function(data) {
    this._contentDiv.empty();
    var newItemP = $('<p></p>').append(this._factory.getBtnCreateItem());
    this._contentDiv.append(newItemP);
    var list = this._appendList('list-items', 10)
    list.buildInboxList(data);
}
