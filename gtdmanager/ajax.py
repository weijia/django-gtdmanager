from django.shortcuts import get_object_or_404, HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST
from dajaxice.decorators import dajaxice_register
from crispy_forms.utils import render_crispy_form
import json
from models import Item
from forms import ItemForm

"""
Forms
"""

def render_to_json(context):
    data = json.dumps(context)
    return HttpResponse(data, {'content_type': 'application/json'})

def get_form(request, item, formClass):
    form = formClass(instance=item)
    form_html = render_crispy_form(form, context=RequestContext(request))
    return render_to_json({'success': True, 'form_html': form_html, 'itemId': item.id})

def handle_form(request, item, formClass, **kwargs):
    data = kwargs or request.POST
    if data.get("argv", None) == "undefined":
        data = None
    form = formClass(data, instance=item)
    if form.is_valid():
        form.save()
        return render_to_json({'success': True})
    form_html = render_crispy_form(form, context=RequestContext(request))
    return render_to_json({'success': False, 'form_html': form_html})

@dajaxice_register(method='GET', name='gtdmanager.item_get_form')
def item_form(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return get_form(request, item, ItemForm)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.item_create')
def item_create(request, **kwargs):
    return handle_form(request, None, ItemForm, **kwargs)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.item_update')
def item_update(request, item_id, **kwargs):
    item = get_object_or_404(Item, pk=item_id)
    return handle_form(request, item, ItemForm, **kwargs)
