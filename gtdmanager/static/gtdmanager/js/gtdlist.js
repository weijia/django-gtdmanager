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

        var parent = $('<td></td>');
        if (item.parent_id) {
            var parentData = $('<a href="' + Django.url('gtdmanager:project_detail', item.parent_id) + '">' +
                             item.parent_name + '</a>');
            parent.append(parentData);
        }
        var main = $('<td></td>');
        main.append(this._factory.getLinkEditItem(item));
        if (buttons) {
            main.append(this._factory.getBtnDeleteItem(item).addClass('pull-right'));
            main.append(this._factory.getBtnCompleteItem(item).addClass('pull-right'));
        }
        row.append(parent);
        row.append(main);
        table.append(row);
    }
    this.div.append(table);
}
