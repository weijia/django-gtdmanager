function GtdControlFactory() {
}

/* Public */

GtdControlFactory.prototype.getBtnCreateContext = function() {
    return this._getBtnCreate('context');
}

GtdControlFactory.prototype.getBtnCreateItem = function() {
    return this._getBtnCreate('item', 'inbox item');
}

GtdControlFactory.prototype.getBtnCompleteItem = function(item) {
    return this._getBtnComplete(item, "item");
}

GtdControlFactory.prototype.getBtnDeleteItem = function(item) {
    return this._getBtnDelete(item, 'item');
}

GtdControlFactory.prototype.getBtnDeleteContext = function(ctx) {
    return this._getBtnDelete(ctx, 'context');
}

GtdControlFactory.prototype.getBtnCleanArchive = function(callback) {
    return $('<button>Remove archived items</button>').addClass('btn btn-danger').click(callback);
}

GtdControlFactory.prototype.getBtnItemReference = function(item, callback) {
    return this._getLinkBtn(item, "item", "reference", "Ref", callback).addClass('btn-primary');
}

GtdControlFactory.prototype.getBtnItemSomeday = function(item, callback) {
    return this._getLinkBtn(item, "item", "someday", "Someday", callback).addClass('btn-primary');
}

GtdControlFactory.prototype.getBtnItemToProject = function(item, callback) {
    return this._getLinkBtn(item, "item", "toproject", "Project", callback).addClass('btn-primary');
}

GtdControlFactory.prototype.getBtnItemWaitfor = function(item, callback) {
    return this._getLinkBtn(item, "item", "waitfor", "Wait", callback).addClass('btn-primary');
}

GtdControlFactory.prototype.getBtnItemRemider = function(item) {
    return this._getLinkEdit(item, "reminder", null, "Remind").addClass('btn-primary');
}

GtdControlFactory.prototype.getBtnItemNext = function(item) {
    return this._getLinkEdit(item, "next", null, "Next").addClass('btn-primary');
}

GtdControlFactory.prototype.getLinkEditItem = function(item, captionName) {
    return this._getLinkEdit(item, 'item', captionName);
}

GtdControlFactory.prototype.getLinkEditContext = function(ctx) {
    return this._getLinkEdit(ctx, 'context');
}

GtdControlFactory.prototype.getLinkEditReminder = function(item) {
    return this._getLinkEdit(item, "reminder");
}

GtdControlFactory.prototype.getLinkEditNext = function(item) {
    return this._getLinkEdit(item, "next");
}

GtdControlFactory.prototype.getContextsSpan = function(item) {
    var ctx_names = "";
    for (var ctx_id in item.contexts) {
        if (item.contexts.hasOwnProperty(ctx_id)) {
            ctx_names += item.contexts[ctx_id] + " ";
        }
    }
    return $('<span>'+ ctx_names+'</span>');
}

/* Private */

GtdControlFactory.prototype._linkBtnBase = function(useBtnTag, item, model, action, text, callback) {
    var html = useBtnTag ? '<button type="button">' + text + '</button>'
                         : '<a href="javascript:void(0);">'+ text + '</a>';

    elm = $(html).click( function(){
            var method = get_dajaxice_method(model, action);
            var params = item ? {'item_id': item.id} : {}
            method(callback, params)
        });

    if (useBtnTag) {
        elm.addClass('btn');
    }
    return elm;
}

GtdControlFactory.prototype._getAjaxLink = function(item, model, action, text, callback) {
    return this._linkBtnBase(false, item, model, action, text, callback );
}

GtdControlFactory.prototype._getLinkBtn = function(item, model, action, text, callback) {
    return this._getAjaxLink(item, model, action, text, callback).addClass('btn btn-sm');
}

GtdControlFactory.prototype._getBtnAction = function(item, caption, model, action, title) {
    var form = new GtdForm(title);
    return this._getLinkBtn(item, model, action, caption, form.display_form.bind(form));
}

GtdControlFactory.prototype._getBtnCreate = function(model, modelCaptionName) {
    captionName = this._getCaptionName(model, modelCaptionName);
    var form = new GtdForm('Create ' + captionName);
    return this._linkBtnBase(true, null, model, 'create', 'Add new ' + captionName,
        form.display_form.bind(form)).addClass('btn-primary');
}

GtdControlFactory.prototype._getBtnComplete = function(item, model) {
    return this._getLinkBtn(item, model, "complete", "Done", complete_callback).addClass('btn-success');
}

GtdControlFactory.prototype._getBtnDelete = function(item, model) {
    return this._getLinkBtn(item, model, "delete", "X", delete_callback).addClass('btn-danger');
}

GtdControlFactory.prototype._getCaptionName = function(model, captionName) {
    return captionName && captionName != undefined ? captionName : model;
}

GtdControlFactory.prototype._getLinkEdit = function(item, model, modelCaptionName, btnCaption) {
    formCaption = "Edit " + this._getCaptionName(model, modelCaptionName);
    bCaption = this._getCaptionName(item.name, btnCaption);
    return this._getBtnAction(item, bCaption, model, "form", formCaption).removeClass('btn btn-sm');
}
