from __future__ import unicode_literals
from django.conf.urls import patterns, url

urlpatterns = patterns('superdesk.views',
    url(r'^$', 'index', name='index'),
    url(r'^article/(?P<guid>.*)$', 'item', name='item'),
)
