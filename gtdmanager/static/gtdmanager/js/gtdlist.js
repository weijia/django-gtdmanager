/**
 * Class for building and manipulating item lists
 * @param {string} divName - id of div in which the list will be built
 */
function GtdList(divName) {
    id = divName[0] == '#' ? divName : '#' + divName;
    this.div = $(id)
    if (this.div.length != 1) {
        console.log("Cannot find div " + id);
        this.div = null;
    }
    this._factory = new GtdControlFactory();
}

GtdList.prototype._buildTable = function(headerData) {
    var table = $('<table></table>').addClass("table table-condensed table-striped");
    var head = $('<thead></thead>');
    var headerRow = $('<tr></tr>');
    for (var name in headerData) {
        if (headerData.hasOwnProperty(name)) {
            headerRow.append($('<th class="col-xs-' + headerData[name] + '">'+ name +'</th>'));
        }
    }
    head.append(headerRow);
    table.append(head);
    return table;
}

GtdList.prototype.buildContexts = function(data, setdefaultClbk) {
    this.div.empty();
    headerData = {"Default": 1, "Name": 3};
    var table = this._buildTable(headerData);

    var attrs = {"type": "radio", "name": "default",
                 "id": null, "value": null, "checked": false}
    for (var i=0; i<data.length; i++) {
        var ctx = data[i];
        var row = $('<tr></tr>');

        var defaultSelector = $('<td></td>');
        attrs.id = "option_default_" + ctx.id;
        attrs.value = ctx.id;
        attrs.checked = ctx.is_default;
        defaultSelector.append( $('<input>').attr(attrs).click(
            Dajaxice.gtdmanager.context_setdefault.bind(this, setdefaultClbk, {'item_id': ctx.id})
        ));
        row.append(defaultSelector);

        var main = $('<td></td>');
        main.append(this._factory.getLinkEditContext(ctx));
        row.append(main);
        main.append(this._factory.getBtnDeleteContext(ctx, 'context').addClass('pull-right'));

        table.append(row);
    }
    this.div.append(table);
}

GtdList.prototype.buildItems = function(data, widths, buttons) {
    this.div.empty();
    headerData = {"Project": widths[0], "Name": widths[1]};
    var table = this._buildTable(headerData);

    for (var i=0; i<data.length; i++) {
        var item = data[i];
        var row = $('<tr></tr>');

        var main = $('<td></td>');
        main.append(this._factory.getLinkEditItem(item));
        if (buttons) {
            main.append(this._factory.getBtnDeleteItem(item).addClass('pull-right btn-table'));
            main.append(this._factory.getBtnCompleteItem(item).addClass('pull-right btn-table'));
        }
        row.append(this._parentTD(item));
        row.append(main);
        table.append(row);
    }
    this.div.append(table);
}

GtdList.prototype.buildInboxList = function(data) {
    var table = this._buildTable({"Project": 2, "Task": 3, "Action": 5});
    for (var i=0; i<data.length; i++) {
        var item = data[i];
        var row = $('<tr></tr>');
        row.append(this._parentTD(item));

        var main = $('<td></td>');
        main.append(this._factory.getLinkEditItem(item));
        row.append(main);

        var actions = $('<td></td>');
        // TODO setup correct callbacks
        actions.append(this._factory.getBtnDeleteItem(item).addClass('btn-table'));
        actions.append(this._factory.getBtnItemReference(item, delete_callback).addClass('btn-table'));
        actions.append(this._factory.getBtnItemSomeday(item, delete_callback).addClass('btn-table'));
        actions.append(this._factory.getBtnItemToProject(item, delete_callback).addClass('btn-table'));
        actions.append(this._factory.getBtnItemWaitfor(item, delete_callback).addClass('btn-table'));
        actions.append(this._factory.getBtnCompleteItem(item).addClass('btn-table'));
        actions.append(this._factory.getBtnItemRemider(item).addClass('btn btn-sm btn-table'));
        actions.append(this._factory.getBtnItemNext(item).addClass('btn btn-sm btn-table'));
        row.append(actions);

        table.append(row);
    }
    this.div.append(table);
}

GtdList.prototype.buildTickler = function(data, dateformat) {
    this.div.empty();

    headerData = {"Project": 2, "Name": 4};
    if (dateformat) {
        headerData["Date"] = "2  centerText";
    } else {
        headerData[""] = "2  centerText";
    }
    var table = this._buildTable(headerData);

    for (var i=0; i<data.length; i++) {
        var item = data[i];
        var row = $('<tr></tr>');
        row.append(this._parentTD(item));

        var main = $('<td></td>');
        main.append(this._factory.getLinkEditReminder(item));
        main.append(this._factory.getBtnDeleteItem(item).addClass('pull-right btn-table'));
        main.append(this._factory.getBtnCompleteItem(item).addClass('pull-right btn-table'));
        row.append(main);

        datetd = $('<td class="centerText"></td>').append( this._formatDate(new Date(item.remind_at), dateformat) );
        row.append(datetd);

        table.append(row);
    }
    this.div.append(table);
}

GtdList.prototype._parentTD = function(item) {
    var parent = $('<td></td>');
    if (item.parent_id) {
        var parentData = $('<a href="' + Django.url('gtdmanager:project_detail', item.parent_id) + '">' +
                         item.parent_name + '</a>');
        parent.append(parentData);
    }
    return parent;
}

// TODO: replace with some sane method
GtdList.prototype._formatDate = function(date, format) {
    var daynames = ["Sun", "Mon", "Tue", "Wen", "Thu", "Fri", "Sat"];
    if (format == "") {
        return "";
    } else if (format == "d.m.Y") {
        return date.getDate() + "." + date.getMonth() + "." + date.getFullYear();
    } else if (format == "l (d.m.)") {
        var dayname = daynames[date.getDay()]
        return dayname + " (" + date.getDate() + "." + date.getMonth() + ".)";
    }

}
