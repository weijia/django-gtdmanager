from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from gtdmanager.forms import ItemForm
from gtdmanager.models import Item

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

def next(request):
    return render_to_response('gtdmanager/next.html', {'btnName': 'next'})