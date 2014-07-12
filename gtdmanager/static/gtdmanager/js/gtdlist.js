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

GtdList.prototype.buildItems = function(data, widths, buttons) {
    this.div.empty();
    var table = $('<table></table>').addClass("table table-condensed table-striped");
    var head = $('<thead>\
                    <tr>\
                        <th class="col-xs-' + widths[0] + '">Project</th>\
                        <th class="col-xs-' + widths[1] + '">Name</th>\
                    </tr>\
                  </thead>');
    table.append(head);

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

GtdList.prototype.getBtnDeleteItem = function(item) {
    return $(
        '<a href="javascript:void(0);"\
            onclick="Dajaxice.gtdmanager.item_delete(delete_callback, {\'item_id\':' + item.id + '})"\
        >X</a>'
    ).addClass('btn btn-danger btn-sm');
}

GtdList.prototype.getFormEditItem = function(item) {
    return $(
        '<a href="javascript:void(0);"\
            onclick="Dajaxice.gtdmanager.item_get_form(display_form.bind(this, \'Edit item\'),\
                {\'item_id\':' + item.id + '})"\
         >' + item.name + '</a>'
    );
}
