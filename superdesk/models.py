from __future__ import unicode_literals
from django.conf import settings
from mongoengine import *
from collections import deque

connect(settings.DATABASE_NAME)

class Ref(EmbeddedDocument):
    idRef = StringField()
    itemClass = StringField()
    residRef = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    contentType = StringField()
    format = StringField()
    generator = StringField()
    width = IntField()
    height = IntField()

class Group(EmbeddedDocument):
    """Group
    """
    role = StringField()
    mode = StringField()
    refs = ListField(EmbeddedDocumentField(Ref))

    def get_items(self):
        refs = []
        for ref in self.refs:
            refs.append(ref)
        return refs

class Content(EmbeddedDocument):
    """Content
    """
    content = StringField()

class Item(Document):
    """anyItem"""

    id = StringField(primary_key=True)
    itemClass = StringField()
    headline = StringField()
    groups = ListField(EmbeddedDocumentField(Group))
    contents = ListField(EmbeddedDocumentField(Content))

    meta = {'collection': 'items'}

    def get_refs(self, role):
        items = []
        queue = deque((role,))
        while len(queue):
            role = queue.popleft()
            refs = []
            for group in self.groups:
                if group.role == role:
                    refs += group.refs
            for ref in refs:
                if ref.idRef:
                    queue.append(ref.idRef)
                else:
                    items.append(ref)
        return items
