from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from gtdmanager.forms import ItemForm
from gtdmanager.models import Item, Project

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

def inbox_edit_item(request, item_id):
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
    
def next(request):
    return render_to_response('gtdmanager/next.html', {'btnName': 'next'})

def project_detail(request, project_id):
    p = get_object_or_404(Project, pk=project_id)
    # get all and split - should be faster than multiple requests with .filter(status=)
    items = p.item_set.all()
    nexts = [item for item in items if item.status == Item.NEXT]
    return render_to_response('gtdmanager/project_detail.html',
            {'p': p, 'nexts': nexts} )