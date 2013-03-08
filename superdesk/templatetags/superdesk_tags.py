from __future__ import unicode_literals
from hashlib import sha1
from bs4 import BeautifulSoup

from django import template
from django.template.base import NodeList, token_kwargs
from django.utils import six
from django.conf import settings
import django.core.files.storage as storages

from superdesk.models import Item

register = template.Library()
storage = storages.FileSystemStorage()

@register.filter
def static_url(value):
    return '%s%s' % (settings.STATIC_URL, value)

@register.filter
def media_url(content):
    """Get media url for given resource
    """
    return storage.url(storage.get_valid_name(content.residRef))

@register.filter
def lead(html):
    lead = html.split("\n")[:2]
    return "\n".join(map(unicode, lead))

@register.assignment_tag(takes_context=True)
def remote_content(context, rendition, **kwargs):
    """Get item remote content
    """
    try:
        item = kwargs['item']
    except KeyError:
        item = context['item']

    if not item or item.itemClass != 'icls:picture':
        return None

    for remote in item.contents:
        if remote.rendition == rendition:
            return remote

@register.assignment_tag(takes_context=True)
def inline_content(context, **kwargs):
    """Get item inline content
    """
    try:
        item = kwargs['item']
    except KeyError:
        item = context['item']

    try:
        soup = BeautifulSoup(item.contents[0].content)
        return "\n".join([unicode(p) for p in soup.body.find_all('p')])
    except:
        return None

@register.assignment_tag(takes_context=True)
def package_items(context, **kwargs):
    item = context['item']
    refs = item.get_refs(kwargs['role'])

    if 'class' in kwargs:
        refs = [ref for ref in refs if ref.itemClass == kwargs['class']]

    if 'limit' in kwargs:
        refs = refs[:kwargs['limit']]

    items = []
    for ref in refs:
        items.append(Item.objects(guid=ref.residRef).first())
    return items

def get_kwargs(parser, token):
    """helper for parsing token kwargs"""
    kwargs = {}
    bits = token.split_contents()
    bits = bits[1:]
    if len(bits):
        kwargs = token_kwargs(bits, parser)
    return kwargs

@register.tag(name="items")
def do_items(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('enditems',))
    parser.delete_first_token()
    return ItemsNode(nodelist, kwargs)

class ItemsNode(template.Node):
    """Items Node
    """
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def resolve_kwargs(self, context):
        return dict([(key, val.resolve(context)) for key, val in six.iteritems(self.kwargs)])

    def render(self, context):
        context.push()
        nodelist = NodeList()
        kwargs = self.resolve_kwargs(context)
        limit = kwargs['limit'] if 'limit' in kwargs else 55
        start = kwargs['start'] if 'start' in kwargs else 0
        order = kwargs['order'] if 'order' in kwargs else '-versionCreated'
        items = Item.objects(itemClass=kwargs['class']).order_by(order)[start:limit]
        for item in items:
            context['item'] = item
            for node in self.nodelist:
                nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)
