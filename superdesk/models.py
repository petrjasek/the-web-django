from __future__ import unicode_literals
from collections import deque
from mongoengine import *

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
    id = StringField()
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
    contenttype = StringField()
    content = StringField()

class Item(Document):
    """anyItem"""

    guid = StringField(unique=True)
    itemClass = StringField()
    headline = StringField()
    slugline = StringField()
    byline = StringField()
    creditline = StringField()
    firstCreated = DateTimeField()
    versionCreated = DateTimeField()

    groups = ListField(EmbeddedDocumentField(Group))
    contents = ListField(EmbeddedDocumentField(Content))

    copyrightHolder = StringField()

    meta = {
        'collection': 'items',
        'allow_inheritance': False,
        'indexes': [('itemClass', '-versionCreated')]
        }

    def get_refs(self, role):
        items = []
        queue = deque((role,))
        while len(queue):
            role = queue.popleft()
            refs = []
            for group in self.groups:
                if group.id == role or group.role == role:
                    refs += group.refs
            for ref in refs:
                if ref.idRef:
                    queue.append(ref.idRef)
                else:
                    items.append(ref)
        return items
