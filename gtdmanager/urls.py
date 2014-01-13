from django.conf.urls import patterns, url
from gtdmanager import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^next$', views.next, name='next'),
    url(r'^inbox/edititem/(?P<item_id>\d+)$', views.inbox_edit_item, name='inbox_edit_item'),
    url(r'^projects/(?P<project_id>\d+)$', views.project_detail, name='project_detail'),
)