from django.conf.urls import patterns, url
from gtdmanager import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^inbox/edit/(?P<item_id>\d+)$', views.inbox_edit_item, name='inbox_edit_item'),
    url(r'^inbox/delete/(?P<item_id>\d+)$', views.inbox_delete_item, name='inbox_delete_item'),
    url(r'^inbox/complete/(?P<item_id>\d+)$', views.inbox_complete_item, name='inbox_complete_item'),
    url(r'^inbox/reference/(?P<item_id>\d+)$', views.inbox_reference_item, name='inbox_reference_item'),
    url(r'^inbox/someday/(?P<item_id>\d+)$', views.inbox_someday_item, name='inbox_someday_item'),
    url(r'^inbox/wait/(?P<item_id>\d+)$', views.inbox_wait_item, name='inbox_wait_item'),
    url(r'^inbox/item_to_project/(?P<item_id>\d+)$', views.inbox_item_to_project, name='inbox_item_to_project'),
    
    url(r'^next$', views.next, name='next'),    
    url(r'^projects/(?P<project_id>\d+)$', views.project_detail, name='project_detail'),
)