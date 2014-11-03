from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('ptl.ui_apps',
    url(r'^$', 'pages.views.homepage', name='homepage'),
    url(r'^dashboard/$', 'dashboard.views.dashboard', name='dashboard'),
    url(r'^dashboard/login/$', 'dashboard.views.login', name='login'),
    url(r'^dashboard/logout/$', 'dashboard.views.logout', name='logout'),
    url(r'^dashboard/confirm/$', 'dashboard.views.confirm', name='confirm'),
)
urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
