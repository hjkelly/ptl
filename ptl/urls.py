from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^dashboard/$', include('ptl.ui_apps.dashboard.urls')),
    url(r'^$', 'ptl.ui_apps.pages.views.homepage'),

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
