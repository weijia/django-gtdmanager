from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def home(request):
    return HttpResponseRedirect(reverse('gtdmanager:next'))

def inbox(request):
    return render_to_response('gtdmanager/inbox.html')

def next(request):
    return render_to_response('gtdmanager/next.html')