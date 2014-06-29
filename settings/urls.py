from django.conf.urls import patterns, include, url
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()

urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^gtdmanager/', include('gtdmanager.urls', namespace="gtdmanager")),
)