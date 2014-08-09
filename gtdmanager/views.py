from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db import connection, transaction
from django.utils import timezone
from datetime import datetime, timedelta, date, time
import json
from django.core.serializers.json import DjangoJSONEncoder

from gtdmanager.models import Item, Project, Context, Next, Reminder
from gtdmanager.forms import ItemForm, ContextForm, NextForm, ReminderForm, ProjectForm

"""
Helpers
"""
def make_unresolved(item, cls):
    item.status = Item.UNRESOLVED
    item.save()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM %s WHERE item_ptr_id = %s" % (cls._meta.db_table, item.id))
    transaction.commit_unless_managed()

"""
Views
"""

def home(request):
    return HttpResponseRedirect(reverse('gtdmanager:next'))

def inbox(request):
    items = [i.to_json(True) for i in Item.objects.filter(status=Item.UNRESOLVED)]
    return render_to_response("gtdmanager/inbox.html",
        {'btnName': 'inbox', 'listData': json.dumps(items, cls = DjangoJSONEncoder)},
        RequestContext(request))

def reminder_to_item(request, item_id, redir_page):
    rem = get_object_or_404(Reminder, pk=item_id)
    make_unresolved(rem, Reminder)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))

def next_to_item(request, item_id, redir_page):
    the_next = get_object_or_404(Next, pk=item_id)
    make_unresolved(the_next, Next)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))

def next(request):
    sort_fn = lambda a,b: cmp(a.contexts.first().name, b.contexts.first().name)
    fetch = Next.objects.unfinished()
    nexts = [r.to_json(True) for r in sorted(fetch, sort_fn)]
    fetch = Reminder.objects.active()
    reminders = [r.to_json(True) for r in sorted(fetch, sort_fn)]
    convert_fn = lambda items: json.dumps(items, cls = DjangoJSONEncoder)
    return render_to_response('gtdmanager/next.html', {'btnName': 'next',
        'nexts': convert_fn(nexts), 'reminders': convert_fn(reminders)})

def projects(request):
    projects = [ p.to_json(True, True) for p in Project.objects.unfinished()]
    return render_to_response('gtdmanager/projects.html',
            {'btnName': 'projects', 'listData': json.dumps(projects, cls = DjangoJSONEncoder) },
            RequestContext(request) )

def project_detail(request, project_id):
    p = get_object_or_404(Project, pk=project_id)
    return render_to_response('gtdmanager/project_detail.html',
            {'p': p, 'btnName': 'projects', 'listData': json.dumps(p.to_json(True, True), cls = DjangoJSONEncoder)},
            RequestContext(request) )

def _itemlist(request, status, contextBase):
    items = [i.to_json(True) for i in Item.objects.filter(status=status)]
    contextBase['listData'] = json.dumps(items, cls = DjangoJSONEncoder)
    return render_to_response('gtdmanager/itemlist.html', contextBase, RequestContext(request))

def waiting(request):
    return _itemlist(request, Item.WAITING_FOR, {'btnName': 'pending', 'header': 'Waiting'})

def someday(request):
    return _itemlist(request, Item.SOMEDAY, {'btnName': 'pending', 'header': 'Someday / Maybe'})

def references(request):
    return _itemlist(request, Item.REFERENCE, {'btnName': 'pending', 'header': 'References'})

def tickler(request):
    reminders = Reminder.objects.unfinished().order_by('remind_at')
    pending = [r for r in reminders if not r.active()] # TODO: test
    tomorrows = []
    this_week = []
    futures = []

    tz = timezone.get_current_timezone()
    tomorrow = (datetime.combine(date.today(), time()) + timedelta(days=2)).replace(tzinfo=tz)
    next_monday_dt = date.today() + timedelta(days=(7 - date.today().weekday()))
    next_monday = datetime.combine(next_monday_dt, time()).replace(tzinfo=tz)
    for rem in pending:
        if rem.remind_at < tomorrow:
            tomorrows.append(rem.to_json(True))
        elif rem.remind_at < next_monday:
            this_week.append(rem.to_json(True))
        else:
            futures.append(rem.to_json(True))

    convert_fn = lambda items: json.dumps(items, cls = DjangoJSONEncoder)
    return render_to_response('gtdmanager/tickler.html',
       {'btnName': 'pending', 'tomorrows': convert_fn(tomorrows), 'this_week': convert_fn(this_week), 'futures': convert_fn(futures)},
        RequestContext(request))

def contexts(request):
    contexts = get_list_or_404(Context)
    items = [ctx.to_json() for ctx in contexts]
    listData = json.dumps(items, cls = DjangoJSONEncoder)
    return render_to_response('gtdmanager/contexts.html', {'btnName': 'manage', 'listData': listData},
                              RequestContext(request))

def archive(request):
    completed = [i.to_json(True) for i in Item.objects.filter(status=Item.COMPLETED)]
    deleted = [i.to_json(True) for i in Item.objects.filter(status=Item.DELETED)]
    return render_to_response("gtdmanager/archive.html",
        {'btnName': 'manage', 'completed': json.dumps(completed, cls = DjangoJSONEncoder),
         'deleted': json.dumps(deleted, cls = DjangoJSONEncoder)}, RequestContext(request))
