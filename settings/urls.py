from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^gtdmanager/', include('gtdmanager.urls', namespace="gtdmanager")),
)