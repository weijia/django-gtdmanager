from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^gtdmanager/', include('gtdmanager.urls', namespace="gtdmanager")),
)