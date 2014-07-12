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
        main.append(this.getFormEditContext(ctx));
        row.append(main);
        main.append(this.getBtnDeleteContext(ctx, 'context').addClass('pull-right'));

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
        main.append(this.getFormEditItem(item));
        if (buttons) {
            main.append(this.getBtnDeleteItem(item).addClass('pull-right'));
            main.append(this.getBtnCompleteItem(item).addClass('pull-right'));
        }
        row.append(parent);
        row.append(main);
        table.append(row);
    }
    this.div.append(table);
}

GtdList.prototype.getBtnCompleteItem = function(item) {
    return $(
        '<a href="javascript:void(0);"\
            onclick="Dajaxice.gtdmanager.item_complete(complete_callback, {\'item_id\':' + item.id + '})"\
        >Done</a>'
    ).addClass('btn btn-success btn-sm');
}

GtdList.prototype._getBtnDelete = function(item, model) {
    return $(
        '<a href="javascript:void(0);"\
            onclick="Dajaxice.gtdmanager.' + model + '_delete(delete_callback, {\'item_id\':' + item.id + '})"\
        >X</a>'
    ).addClass('btn btn-danger btn-sm');
}

GtdList.prototype.getBtnDeleteItem = function(item) {
    return this._getBtnDelete(item, 'item');
}

GtdList.prototype.getBtnDeleteContext = function(ctx) {
    return this._getBtnDelete(ctx, 'context');
}

GtdList.prototype._getEditForm = function(item, model) {
    return $(
        '<a href="javascript:void(0);"\
            onclick="Dajaxice.gtdmanager.' + model + '_get_form(\
                display_form.bind(this, \'Edit ' + model + '\'), {\'item_id\':' + item.id + '}\
            )"\
         >' + item.name + '</a>'
    );
}

GtdList.prototype.getFormEditItem = function(item) {
    return this._getEditForm(item, 'item');
}

GtdList.prototype.getFormEditContext = function(ctx) {
    return this._getEditForm(ctx, 'context');
}