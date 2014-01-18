from django.conf.urls import patterns, url
from gtdmanager import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^item/(?P<item_id>\d+)/edit$', views.inbox_item_edit, name='inbox_item_edit'),
    url(r'^item/(?P<item_id>\d+)/delete$', views.item_delete, name='item_delete'),
    url(r'^item/(?P<item_id>\d+)/complete$', views.item_complete, name='item_complete'),
    url(r'^item/(?P<item_id>\d+)/reference$', views.item_reference, name='item_reference'),
    url(r'^item/(?P<item_id>\d+)/someday$', views.item_someday, name='item_someday'),
    url(r'^item/(?P<item_id>\d+)/wait$', views.item_wait, name='item_wait'),
    url(r'^item/(?P<item_id>\d+)/to_project$', views.item_to_project, name='item_to_project'),
    
    url(r'^next$', views.next, name='next'),
    url(r'^projects/(?P<project_id>\d+)$', views.project_detail, name='project_detail'),
)
