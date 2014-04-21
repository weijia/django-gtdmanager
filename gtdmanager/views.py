from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db import connection, transaction
from django.utils import timezone
from datetime import datetime, timedelta, date, time

from gtdmanager.models import Item, Project, Context, Next, Reminder
from gtdmanager.forms import ItemForm, ContextForm, NextForm, ReminderForm, ProjectForm

"""
Helpers
"""
def change_item_status(item_id, new_status):
    item = get_object_or_404(Item, pk=item_id)
    if new_status == Item.COMPLETED:
        item.complete()
    elif new_status == Item.DELETED:
        item.gtddelete()
    else:
        item.status = new_status
        item.save()

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
    items = Item.objects.filter(status=Item.UNRESOLVED)
    return render_to_response('gtdmanager/inbox.html', { 'btnName': 'inbox', 'items' : items },
                              RequestContext(request))

def item_reference(request, item_id):
    change_item_status(item_id, Item.REFERENCE)
    return HttpResponseRedirect(reverse('gtdmanager:inbox'))

def item_someday(request, item_id):
    change_item_status(item_id, Item.SOMEDAY)
    return HttpResponseRedirect(reverse('gtdmanager:inbox'))

def item_wait(request, item_id):
    change_item_status(item_id, Item.WAITING_FOR)
    return HttpResponseRedirect(reverse('gtdmanager:inbox'))

def item_to_project(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    project = Item.objects.convertTo(Project, item)
    project.save()
    return HttpResponseRedirect(reverse('gtdmanager:project_detail', args=(item.id,)))

def reminder_to_item(request, item_id, redir_page):
    rem = get_object_or_404(Reminder, pk=item_id)
    make_unresolved(rem, Reminder)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))
    
def next_to_item(request, next_id, redir_page):
    the_next = get_object_or_404(Next, pk=next_id)
    make_unresolved(the_next, Next)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))

def next(request):
    sort_fn = lambda a,b: cmp(a.contexts.first().name, b.contexts.first().name)
    fetch = Next.objects.unfinished()
    nexts = sorted(fetch, sort_fn)
    fetch = Reminder.objects.active()
    reminders = sorted(fetch, sort_fn)
    return render_to_response('gtdmanager/next.html', {'btnName': 'next', 
        'nexts': nexts, 'reminders': reminders})

def projects(request):
    projects = Project.objects.unfinished()
    return render_to_response('gtdmanager/projects.html',
            {'btnName': 'projects', 'projects': projects, }, RequestContext(request) )

def project_detail(request, project_id):
    p = get_object_or_404(Project, pk=project_id)
    nexts = p.nexts(True)
    reminders = p.reminders(True)
    subs = p.subprojects(True)
    waiting = p.item_set.filter(status=Item.WAITING_FOR)
    somedays = p.item_set.filter(status=Item.SOMEDAY)
    refs = p.item_set.filter(status=Item.REFERENCE)
    completed = p.item_set.filter(status=Item.COMPLETED)
    deleted = p.item_set.filter(status=Item.DELETED)
    return render_to_response('gtdmanager/project_detail.html',
            {'p': p, 'btnName': 'projects', 'nexts': nexts, 'reminders': reminders, 'subprojects': subs, 
             'waiting': waiting, 'somedays': somedays, 'references': refs, 'completed': completed,
             'deleted': deleted}, RequestContext(request) )

def waiting(request):
    waiting = Item.objects.filter(status=Item.WAITING_FOR)
    return render_to_response('gtdmanager/itemlist.html',
       {'btnName': 'pending', 'header': 'Waiting', 'redir_page': 'waiting', 'items': waiting},
        RequestContext(request))

def tickler(request):
    reminders = Reminder.objects.unfinished().order_by('remind_at')
    pending = [r for r in reminders if not r.active()]
    tomorrows = []
    this_week = []
    futures = []
    
    tz = timezone.get_current_timezone()
    tomorrow = (datetime.combine(date.today(), time()) + timedelta(days=2)).replace(tzinfo=tz)
    next_monday_dt = date.today() + timedelta(days=(7 - date.today().weekday()))
    next_monday = datetime.combine(next_monday_dt, time()).replace(tzinfo=tz)
    for rem in pending:
        if rem.remind_at < tomorrow:
            tomorrows.append(rem)
        elif rem.remind_at < next_monday:
            this_week.append(rem)
        else:
            futures.append(rem)

    return render_to_response('gtdmanager/tickler.html',
       {'btnName': 'pending', 'tomorrows': tomorrows, 'this_week': this_week, 'futures': futures},
        RequestContext(request))
    
def someday(request):
    items = Item.objects.filter(status=Item.SOMEDAY)
    return render_to_response('gtdmanager/itemlist.html',
       {'btnName': 'pending', 'header': 'Someday / Maybe', 'redir_page': 'someday', 'items': items},
        RequestContext(request))

def references(request):
    items = Item.objects.filter(status=Item.REFERENCE)
    return render_to_response('gtdmanager/itemlist.html',
        {'btnName': 'pending', 'header': 'References', 'redir_page': 'references', 'items': items},
        RequestContext(request))

def contexts(request):
    contexts = get_list_or_404(Context)
    
    if request.method == "POST":
        form = ContextForm(request.POST)
        if form.is_valid():
            form.save()
            form = ContextForm()
            return HttpResponseRedirect(reverse('gtdmanager:contexts'))
    else:
        form = ContextForm()
    return render_to_response('gtdmanager/contexts.html',
        {'btnName': 'manage', 'contexts': contexts, 'form': form}, RequestContext(request))

def context_set_default(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    context.is_default = True
    context.save()
    return HttpResponseRedirect(reverse('gtdmanager:contexts'))

def archive(request):
    completed = Item.objects.filter(status=Item.COMPLETED)
    deleted = Item.objects.filter(status=Item.DELETED)
    return render_to_response("gtdmanager/archive.html",
        {'btnName': 'manage', 'completed': completed, 'deleted': deleted},
        RequestContext(request))

def archive_clean(request):
    Item.objects.filter(status__in=(Item.COMPLETED, Item.DELETED)).delete()
    return HttpResponseRedirect(reverse('gtdmanager:archive'))
