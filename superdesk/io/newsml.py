from __future__ import unicode_literals
import xml.etree.ElementTree as etree
import datetime

import superdesk.models as models

class Parser():
    """NewsMl xml parser"""

    XMLNS = 'http://iptc.org/std/nar/2006-10-01/'
    NSMAP = {'iptc': XMLNS}

    def parse_message(self, tree):
        """Parse NewsMessage."""
        items = []
        for item_tree in tree.find(self.qname('itemSet')):
            item = self.parse_item(item_tree)
            items.append(item)
        return items

    def parse_item(self, tree):
        """Parse given xml"""

        item = models.Item()
        item.guid = tree.attrib['guid']
        item.version = int(tree.attrib['version'])

        self.parse_item_meta(tree, item)
        self.parse_content_meta(tree, item)
        self.parse_rights_info(tree, item)

        if item.is_package():
            self.parse_group_set(tree, item)
        else:
            self.parse_content_set(tree, item)

        return item

    def parse_item_meta(self, tree, item):
        """Parse itemMeta tag"""
        meta = tree.find(self.qname('itemMeta'))
        item.itemClass = meta.find(self.qname('itemClass')).attrib['qcode']
        item.provider = meta.find(self.qname('provider')).attrib['literal']
        item.versionCreated = self.datetime(meta.find(self.qname('versionCreated')).text)
        item.firstCreated = self.datetime(meta.find(self.qname('firstCreated')).text)

    def parse_content_meta(self, tree, item):
        """Parse contentMeta tag"""
        meta = tree.find(self.qname('contentMeta'))
        keys = ['urgency', 'slugline', 'headline', 'creditline', 'description']
        for key in keys:
            elem = meta.find(self.qname(key))
            if elem is not None:
                setattr(item, key, elem.text)

    def parse_rights_info(self, tree, item):
        """Parse Rights Info tag"""
        info = tree.find(self.qname('rightsInfo'))
        item.copyrightHolder = info.find(self.qname('copyrightHolder')).attrib['literal']
        item.copyrightNotice = info.find(self.qname('copyrightNotice')).text

    def parse_group_set(self, tree, item):
        for group in tree.find(self.qname('groupSet')):
            data = {}
            data['id'] = group.attrib['id']
            data['role'] = group.attrib['role']
            data['refs'] = self.parse_refs(group)
            item.groups.append(models.Group(**data))

    def parse_refs(self, group):
        refs = []
        for tree in group:
            if 'idref' in tree.attrib:
                refs.append(models.Ref(idref=tree.attrib['idref']))
            else:
                ref = models.Ref()
                ref.residref = tree.attrib['residref']
                ref.contenttype = tree.attrib['contenttype']
                ref.itemClass = tree.find(self.qname('itemClass')).attrib['qcode']
                ref.provider = tree.find(self.qname('provider')).attrib['literal']

                for headline in tree.findall(self.qname('headline')):
                    ref.headline = headline.text

                refs.append(ref)
        return refs

    def parse_content_set(self, tree, item):
        for content in tree.find(self.qname('contentSet')):
            if content.tag == self.qname('inlineXML'):
                data = self.parse_inline_content(content)
            else:
                data = self.parse_remote_content(content)
            item.contents.append(models.Content(**data))

    def parse_inline_content(self, content):
        data = {}
        html = content.find('{http://www.w3.org/1999/xhtml}html')
        etree.register_namespace('', 'http://www.w3.org/1999/xhtml')
        data['contenttype'] = content.attrib['contenttype']
        data['content'] = etree.tostring(html).decode('utf-8')
        return data

    def parse_remote_content(self, content):
        data = {}
        data['residref'] = content.attrib['residref']
        data['size'] = int(content.attrib['size'])
        data['rendition'] = content.attrib['rendition']
        data['contenttype'] = content.attrib['contenttype']
        data['href'] = content.attrib['href']
        return data

    def get_texts(self, elem, keys):
        data = {}
        for key in keys:
            try:
                data[key] = self.find(elem, key).text
            except AttributeError:
                data[key] = None
        return data

    def find(self, elem, match):
        return elem.find('.//iptc:%s' % match, namespaces=self.NSMAP)

    def qname(self, tag):
        return str(etree.QName(self.XMLNS, tag))

    def datetime(self, string):
        return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.000Z')

