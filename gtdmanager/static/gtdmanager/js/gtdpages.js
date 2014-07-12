
/**
 *  Class for building pages in JS
 */
function GtdPages(divName) {
    this._contentDiv = $('#content');
    if (this._contentDiv.length != 1) {
        console.log("Cannot find content div");
        this.div = null;
    }
}

GtdPages.prototype.displayError = function(msg) {
    alert(msg);
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
    this._contentDiv.append($('<div id="'+ divName + '" class="col-xs-8"></div>'));
    var list = new GtdList(divName);
    list.buildItems(listData, [2, 3], false);
}

GtdPages.prototype.buildArchive = function(completed, deleted) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Archive</h1>'));

    if (completed.length || deleted.length) {
        btn = $('<button>Remove archived items</button>').addClass('btn btn-danger').click(this.confirm_clean.bind(this));
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
