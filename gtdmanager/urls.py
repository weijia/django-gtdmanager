from django.conf.urls import patterns, url
from gtdmanager import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^item/(?P<item_id>\d+)/edit/(?P<redir_page>\w+)$', views.item_edit, name='item_edit'),
    url(r'^item/(?P<item_id>\d+)/delete/(?P<redir_page>\w+)$', views.item_delete, name='item_delete'),
    url(r'^item/(?P<item_id>\d+)/complete/(?P<redir_page>\w+)$', views.item_complete, name='item_complete'),
    url(r'^item/(?P<item_id>\d+)/reference$', views.item_reference, name='item_reference'),
    url(r'^item/(?P<item_id>\d+)/someday$', views.item_someday, name='item_someday'),
    url(r'^item/(?P<item_id>\d+)/wait$', views.item_wait, name='item_wait'),
    url(r'^item/(?P<item_id>\d+)/to_project$', views.item_to_project, name='item_to_project'),
    
    url(r'^next$', views.next, name='next'),
    url(r'^next/(?P<item_id>\d+)/edit/(?P<redir_page>\w+)$', views.next_edit, name='next_edit'),
    url(r'^next/(?P<next_id>\d+)/to_item/(?P<redir_page>\w+)$', views.next_to_item, name='next_to_item'),
    
    url(r'^reminder/(?P<item_id>\d+)/edit/(?P<redir_page>\w+)$', views.reminder_edit, name='reminder_edit'),
    url(r'^reminder/(?P<item_id>\d+)/to_item/(?P<redir_page>\w+)$', views.reminder_to_item, name='reminder_to_item'),
    
    url(r'^projects/(?P<project_id>\d+)$', views.project_detail, name='project_detail'),
    
    url(r'^waiting$', views.waiting, name='waiting'),
    url(r'^references', views.references, name='references'),

    url(r'^contexts$', views.contexts, name='contexts'),
    url(r'^contexts/(?P<ctx_id>\d+)/edit$', views.context_edit, name='context_edit'),
    url(r'^contexts/(?P<ctx_id>\d+)/delete$', views.context_delete, name='context_delete'),
    url(r'^contexts/(?P<ctx_id>\d+)/setdefault$', views.context_set_default, name='context_set_default'),
)
