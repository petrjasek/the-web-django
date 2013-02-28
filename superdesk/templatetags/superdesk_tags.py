from __future__ import unicode_literals
from hashlib import sha1
from bs4 import BeautifulSoup
from django import template
from django.template.base import NodeList, token_kwargs
from django.utils import six
from superdesk.models import Item

register = template.Library()

@register.filter
def media_url(value):
    """Get media url for given resource
    """
    return "http://localhost:8080/reuters-php/web/media/%s" % sha1(value).hexdigest()

@register.assignment_tag(takes_context=True)
def remote_content(context, rendition, **kwargs):
    """Get item remote content
    """
    try:
        item = kwargs['item']
    except KeyError:
        item = context['item']
    for remote in item.contentSet.remoteContent:
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
    soup = BeautifulSoup(item.contentSet.inlineContent.content)
    return "\n".join([unicode(p) for p in soup.body.find_all('p')])

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

@register.tag(name="news")
def do_news(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('endnews',))
    parser.delete_first_token()
    return NewsNode(nodelist, kwargs)

@register.tag(name="groups")
def do_groups(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('endgroups',))
    parser.delete_first_token()
    return GroupsNode(nodelist, kwargs)

@register.tag(name="item")
def do_item(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('enditem',))
    parser.delete_first_token()
    return ItemNode(nodelist, kwargs)

class Node(template.Node):

    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def resolve_kwargs(self, context):
        return dict([(key, val.resolve(context)) for key, val in six.iteritems(self.kwargs)])

class GroupsNode(Node):
    def render(self, context):
        context.push()
        kwargs = self.resolve_kwargs(context)
        nodelist = NodeList()
        for group in context['item'].get_groups(kwargs['role']):
            context['group'] = group
            for node in self.nodelist:
                nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)

class ItemNode(Node):
    def render(self, context):
        context.push()
        kwargs = self.resolve_kwargs(context)
        nodelist = NodeList()
        context['package'] = context['item']
        context['item'] = context['group'].get_item(kwargs['class'])
        for node in self.nodelist:
            nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)

class ItemsNode(Node):
    """Items Node
    """

    def render(self, context):
        context.push()
        kwargs = self.resolve_kwargs(context)
        if 'role' in kwargs:
            context['package'] = context['item']
            items = []
            refs = context['package'].get_items(kwargs['role'])
            for ref in refs:
                items.append(Item.objects(id=ref.residref).first())
        else:
            items = Item.objects(itemClass=kwargs['class'])
        nodelist = NodeList()
        for item in items:
            context['item'] = item
            for node in self.nodelist:
                nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)

class NewsNode(Node):
    """News Node
    """

    def render(self, context):
        context.push()
        kwargs = self.resolve_kwargs(context)

        nodelist = NodeList()
        refs = context['item'].get_refs(kwargs['role'])
        for ref in refs:
            print(ref)
            item = Item.objects(id=ref.residRef).first()
            context['item'] = item
            if item.itemClass == 'icls:text':
                soup = BeautifulSoup(item.contents[0].content)
                context['content'] = "\n".join([unicode(p) for p in soup.body.find_all('p')])
            for node in self.nodelist:
                nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)
