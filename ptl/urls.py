from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('ptl.ui_apps',
    url(r'^$', 'pages.views.homepage', name='homepage'),
    url(r'^dashboard/$', 'dashboard.views.dashboard', name='dashboard'),
    url(r'^dashboard/confirm/$', 'dashboard.views.confirm', name='confirm'),
)
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^dashboard/login/$', 'login', name='login'),
    url(r'^dashboard/logout/$', 'logout', name='logout'),
)
urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
