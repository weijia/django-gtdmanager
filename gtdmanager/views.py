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
def change_item_status(item_id, new_status, cls = Item):
    item = get_object_or_404(cls, pk=item_id)
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
    show_form = False
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            form = ItemForm()
            HttpResponseRedirect(reverse('gtdmanager:inbox'))
        else:
            show_form = True
    else:
        form = ItemForm()

    items = Item.objects.filter(status=Item.UNRESOLVED)
    return render_to_response('gtdmanager/inbox.html', context_instance=RequestContext(request), 
        dictionary={ 'btnName': 'inbox', 'form': form, 'show_form' : show_form, 'items' : items })

def _item_edit(request, item_id, redir_page, args=()):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=args))
    else:
        form = ItemForm(instance=item)
        
    return render_to_response("gtdmanager/edititem.html",
        {'form': form, 'edit': True, 'cancel_url': reverse('gtdmanager:'+redir_page, args=args)},
        RequestContext(request))

def item_edit(request, item_id, redir_page):
    return _item_edit(request, item_id, redir_page)

def item_edit_redir_id(request, item_id, redir_page, redir_id):
    return _item_edit(request, item_id, redir_page, (redir_id,))

def item_delete(request, item_id, redir_page):
    change_item_status(item_id, Item.DELETED)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page))

def item_delete_redir_id(request, item_id, redir_page, redir_id):
    change_item_status(item_id, Item.DELETED)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=(redir_id,)))

def item_complete(request, item_id, redir_page):
    change_item_status(item_id, Item.COMPLETED)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))

def item_complete_redir_id(request, item_id, redir_page, redir_id):
    change_item_status(item_id, Item.COMPLETED)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=(redir_id,)))

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

def _reminder_edit(request, item_id, redir_page, args=()):
    cancel_url = reverse('gtdmanager:' + redir_page, args=args)
    try:
        item = Reminder.objects.get(pk=item_id)
    except:
        item = get_object_or_404(Item, pk=item_id)
        item = Item.objects.convertTo(Reminder, item)
        item.save()
        cancel_url = reverse('gtdmanager:reminder_to_item', args=(item_id, redir_page))

    if request.method == "POST":
        form = ReminderForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:'+redir_page))
    else:
        form = ReminderForm(instance=item)
        
    return render_to_response("gtdmanager/edititem.html",
        {'form': form, 'title': 'Edit reminder', 'edit': True, 'cancel_url': cancel_url}, RequestContext(request))

def reminder_edit(request, item_id, redir_page):
    return _reminder_edit(request, item_id, redir_page)

def reminder_edit_redir_id(request, item_id, redir_page, redir_id):
    return _reminder_edit(request, item_id, redir_page, (redir_id,))

def reminder_to_item(request, item_id, redir_page):
    rem = get_object_or_404(Reminder, pk=item_id)
    make_unresolved(rem, Reminder)
    return HttpResponseRedirect(reverse('gtdmanager:' + redir_page))

def _next_edit(request, item_id, redir_page, args=()):
    cancel_url = reverse('gtdmanager:' + redir_page, args=args)
    try:
        item = Next.objects.get(pk=item_id)
    except:
        item = get_object_or_404(Item, pk=item_id)
        item = Item.objects.convertTo(Next, item)
        item.save()
        cancel_url = reverse('gtdmanager:next_to_item', args=(item_id, redir_page))

    if request.method == "POST":
        form = NextForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=args))
    else:
        form = NextForm(instance=item)
        
    return render_to_response("gtdmanager/edititem.html",
        {'form': form, 'editDivPrefix': "next", 'cancel_url': cancel_url, 'edit': True}, RequestContext(request))

def next_edit(request, item_id, redir_page):
    return _next_edit(request, item_id, redir_page)

def next_edit_redir_id(request, item_id, redir_page, redir_id):
    return _next_edit(request, item_id, redir_page, args=(int(redir_id),))
    
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

def _project_edit(request, project_id, redir_page, args=()):
    item = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        print request.POST
        form = ProjectForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=args))
    else:
        form = ProjectForm(instance=item)
        
    return render_to_response("gtdmanager/edititem.html",
        {'form': form, 'title': 'Edit project', 'edit': True, 'cancel_url': reverse('gtdmanager:'+redir_page, args=args)},
        RequestContext(request))

def project_edit(request, project_id):
    return _project_edit(request, project_id, 'project_detail', (int(project_id),))

def project_edit_redir_id(request, project_id, redir_page, redir_id):
    return _project_edit(request, project_id, redir_page, (redir_id,))

def project_complete(request, project_id, redir_page):
    change_item_status(project_id, Item.COMPLETED, Project)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page))

def project_complete_redir_id(request, project_id, redir_page, redir_id):
    change_item_status(project_id, Item.COMPLETED, Project)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=(redir_id,)))

def project_delete(request, project_id, redir_page):
    change_item_status(project_id, Item.DELETED, Project)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page))

def project_delete_redir_id(request, project_id, redir_page, redir_id):
    change_item_status(project_id, Item.DELETED, Project)
    return HttpResponseRedirect(reverse('gtdmanager:'+redir_page, args=(redir_id,)))

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

def context_edit(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    if request.method == "POST":
        form = ContextForm(request.POST, instance=context)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:contexts'))
    else:
        form = ContextForm(instance=context)
        
    return render_to_response("gtdmanager/edititem.html",
        {'form': form, 'title': "Edit context", 'edit': True, 'cancel_url': reverse('gtdmanager:contexts')}, RequestContext(request))

def context_set_default(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    context.is_default = True
    context.save()
    return HttpResponseRedirect(reverse('gtdmanager:contexts'))

def context_delete(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    context.delete()
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
