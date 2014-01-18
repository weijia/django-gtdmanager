from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db import connection, transaction

from gtdmanager.models import Item, Project, Context, Next
from gtdmanager.forms import ItemForm, ContextForm, NextForm

"""
Helpers
"""
def change_item_status(item_id, new_status):
    item = get_object_or_404(Item, pk=item_id)
    item.status = new_status
    item.save()
    return HttpResponseRedirect(reverse('gtdmanager:inbox'))

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
        dictionary={ 'btnName': 'inbox', 'itemform': form, 'show_form' : show_form, 'items' : items })

def inbox_item_edit(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:inbox'))
    else:
        form = ItemForm(instance=item)
        
    return render_to_response("gtdmanager/edititem.html",
        {'itemform': form, 'editDivPrefix': "item"}, RequestContext(request))

def item_delete(request, item_id):
    return change_item_status(item_id, Item.DELETED)

def item_complete(request, item_id):
    return change_item_status(item_id, Item.COMPLETED)

def item_reference(request, item_id):
    return change_item_status(item_id, Item.REFERENCE)

def item_someday(request, item_id):
    return change_item_status(item_id, Item.SOMEDAY)

def item_wait(request, item_id):
    return change_item_status(item_id, Item.WAITING_FOR)

def item_to_project(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    project = Item.objects.convertTo(Project, item)
    project.save()
    return HttpResponseRedirect(reverse('gtdmanager:project_detail', args=(item.id,)))

def inbox_next_edit(request, item_id):
    try:
        item = Next.objects.get(pk=item_id)
    except:
        item = get_object_or_404(Item, pk=item_id)
        item = Item.objects.convertTo(Next, item)

    print item
    if request.method == "POST":
        form = NextForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gtdmanager:inbox'))
    else:
        form = NextForm(instance=item)
        
    return render_to_response("gtdmanager/editnext.html",
        {'itemform': form, 'editDivPrefix': "next",
         'cancel_url': reverse('gtdmanager:inbox_next_to_item', args=(item_id,))},
        RequestContext(request))

def next(request):
    return render_to_response('gtdmanager/next.html', {'btnName': 'next'})

def inbox_next_to_item(request, next_id):
    the_next = get_object_or_404(Next, pk=next_id)
    make_unresolved(the_next, Next)
    return HttpResponseRedirect(reverse('gtdmanager:inbox'))

def project_detail(request, project_id):
    p = get_object_or_404(Project, pk=project_id)
    # get all and split - should be faster than multiple requests with .filter(status=)
    items = p.item_set.all()
    nexts = [item for item in items if item.status == Item.NEXT]
    return render_to_response('gtdmanager/project_detail.html',
            {'p': p, 'nexts': nexts, 'btnName': 'projects',} )

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
        
    return render_to_response("gtdmanager/editcontext.html",
        {'form': form, 'editDivPrefix': "context"}, RequestContext(request))

def context_set_default(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    context.is_default = True
    context.save()
    return HttpResponseRedirect(reverse('gtdmanager:contexts'))

def context_delete(request, ctx_id):
    context = get_object_or_404(Context, pk=ctx_id)
    context.delete()
    return HttpResponseRedirect(reverse('gtdmanager:contexts'))
