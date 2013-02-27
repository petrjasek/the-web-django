from __future__ import unicode_literals
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^', include('superdesk.urls')),
)
