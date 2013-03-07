from __future__ import unicode_literals

from django.utils import unittest

from superdesk.models import Item, Group, Ref

class ItemTest(unittest.TestCase):
    def setUp(self):
        self.item = Item(groups=[
            Group(role='main', refs=[
                Ref(),
                Ref(),
            ]),
            Group(role='sidebars', refs=[
                Ref(idRef='sidebar_0'),
                Ref(idRef='sidebar_1'),
            ]),
            Group(role='sidebar_0', refs=[
                Ref(),
                Ref(),
            ]),
            Group(role='sidebar_1', refs=[
                Ref(),
                Ref(),
            ]),
        ])

    def test_get_refs(self):
        items = self.item.get_refs('nonexisting')
        self.assertEquals(0, len(items))

    def test_get_items_main(self):
        items = self.item.get_refs('main')
        self.assertEquals(2, len(items))

    def test_get_items_sidebars(self):
        items = self.item.get_refs('sidebars')
        self.assertEquals(4, len(items))
