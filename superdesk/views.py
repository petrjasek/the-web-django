from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.http import Http404
from superdesk.models import Item

def index(request):
    return render_to_response('index.html')

def item(request, guid):
    try:
        item = Item.objects.get(guid=guid)
    except Item.DoesNotExist:
        raise Http404
    return render_to_response('item.html', {'item': item})
