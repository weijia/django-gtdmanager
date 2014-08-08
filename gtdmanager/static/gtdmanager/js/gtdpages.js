
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


GtdPages.prototype._ticklerTable = function (title, divName, listData, withDate) {
    this._contentDiv.append($('<h2>' + title + '</h2>'));
    var list = this._appendList(divName, 8)
    list.buildTickler(listData, withDate);
}

GtdPages.prototype._contextItemTable = function (tableName, divName, data, isReminder) {
    this._contentDiv.append($('<h2>' + tableName + '</h2>'));
    var list = this._appendList(divName, 8)
    list.buildContextItem(data, isReminder);
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


GtdPages.prototype.buildNext = function(nexts, reminders) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Next</h1>'));
     if (reminders.length) {
        this._contextItemTable('Reminders', 'list-items-reminder', reminders, true);
        this._contentDiv.append($('<div class="clearDiv" />'));
    }
    if (nexts.length) {
        this._contextItemTable('Nexts', 'list-items-next', nexts, false);
        this._contentDiv.append($('<div class="clearDiv" />'));
    }

}

GtdPages.prototype.buildTickler = function(tomorrows, this_week, futures) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Tickler</h1>'));
    if (tomorrows.length + this_week.length + futures.length == 0) {
        this._contentDiv.append($('<span> No tickler found</span>'));
    } else {
        if (tomorrows.length) {
            this._ticklerTable("Tomorrow", 'list-items-tomorrow', tomorrows, "");
            this._contentDiv.append($('<div class="clearDiv" />'));
        }
        if (this_week.length) {
            this._ticklerTable("This week", 'list-items-thisweek', this_week, "l (d.m.)");
            this._contentDiv.append($('<div class="clearDiv" />'));
        }
        if (futures.length) {
            this._ticklerTable("Future", 'list-items-future', futures, "d.m.Y");
        }
    }
}

GtdPages.prototype.buildProjects = function(data) {
    this._contentDiv.empty();
    this._contentDiv.append($('<h1>Projects</h1>'));
    if (data.length) {
        var list = this._appendList('list-projects', 8)
        list.buildProjects(data);
    } else {
        this._contentDiv.append($('<p>No project found</p>'));
    }
}
