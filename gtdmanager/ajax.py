from django.shortcuts import get_object_or_404, HttpResponse
from django.template import RequestContext
from django.views.decorators.http import require_POST
from dajaxice.decorators import dajaxice_register
from crispy_forms.utils import render_crispy_form
import json
from models import Item, Reminder, Next, Project, Context
from forms import ItemForm, ReminderForm, NextForm, ProjectForm, ContextForm

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
    # kwargs is here for Dajaxice support
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

@dajaxice_register(method='GET', name='gtdmanager.reminder_get_form')
def reminder_form(request, item_id):
    reminder = Reminder.objects.get_or_convert(item_id, Reminder)
    return get_form(request, reminder, ReminderForm)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.reminder_create')
def reminder_create(request, **kwargs):
    return handle_form(request, None, ReminderForm, **kwargs)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.reminder_update')
def reminder_update(request, item_id, **kwargs):
    item = Reminder.objects.get_or_convert(item_id, Reminder)
    return handle_form(request, item, ReminderForm, **kwargs)

@dajaxice_register(method='GET', name='gtdmanager.next_get_form')
def next_form(request, item_id):
    nxt = Next.objects.get_or_convert(item_id, Next)
    return get_form(request, nxt, NextForm)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.next_create')
def next_create(request, **kwargs):
    return handle_form(request, None, NextForm, **kwargs)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.next_update')
def next_update(request, item_id, **kwargs):
    item = Next.objects.get_or_convert(item_id, Next)
    return handle_form(request, item, NextForm, **kwargs)

@dajaxice_register(method='GET', name='gtdmanager.project_get_form')
def project_form(request, item_id):
    p = Project.objects.get_or_convert(item_id, Project)
    return get_form(request, p, ProjectForm)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.project_create')
def project_create(request, **kwargs):
    return handle_form(request, None, ProjectForm, **kwargs)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.project_update')
def project_update(request, item_id, **kwargs):
    p = Project.objects.get_or_convert(item_id, Project)
    return handle_form(request, p, ProjectForm, **kwargs)

@dajaxice_register(method='GET', name='gtdmanager.context_get_form')
def context_form(request, item_id):
    ctx = get_object_or_404(Context, pk=item_id)
    return get_form(request, ctx, ContextForm)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.context_create')
def context_create(request, **kwargs):
    return handle_form(request, None, ContextForm, **kwargs)

@require_POST
@dajaxice_register(method='POST', name='gtdmanager.context_update')
def context_update(request, item_id, **kwargs):
    ctx = get_object_or_404(Context, pk=item_id)
    return handle_form(request, ctx, ContextForm, **kwargs)

@dajaxice_register(method='GET', name='gtdmanager.item_delete')
def item_delete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item.gtddelete()
    return render_to_json({"success": True})

@dajaxice_register(method='GET', name='gtdmanager.project_delete')
def project_delete(request, item_id):
    p = get_object_or_404(Project, pk=item_id)
    p.gtddelete()
    return render_to_json({"success": True})

@dajaxice_register(method='GET', name='gtdmanager.context_delete')
def context_delete(request, item_id):
    context = get_object_or_404(Context, pk=item_id)
    context.delete()
    return render_to_json({"success": True})

@dajaxice_register(method='GET', name='gtdmanager.item_complete')
def item_complete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item.complete()
    return render_to_json({"success": True})

@dajaxice_register(method='GET', name='gtdmanager.project_complete')
def project_complete(request, item_id):
    p = get_object_or_404(Project, pk=item_id)
    p.complete()
    return render_to_json({"success": True})
