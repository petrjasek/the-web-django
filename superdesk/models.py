from django.conf import settings
from mongoengine import *

connect(settings.TEST_DB)

class Ref(EmbeddedDocument):
    itemClass = StringField()
    residref = StringField()
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

    def get_item(self, itemClass):
        for ref in self.refs:
            if ref.itemClass == itemClass:
                return ref

class Item(Document):
    """anyItem"""

    id = StringField(primary_key=True)
    itemClass = StringField()
    headline = StringField()
    groups = ListField(EmbeddedDocumentField(Group))

    meta = {'collection': 'items'}

    def get_groups(self, role):
        groups = []
        for group in self.groups:
            if group.role == role:
                groups.append(group)
        return groups

    def get_items(self, kwargs):
        items = []
        return items
