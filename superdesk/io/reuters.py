import os
import requests
import xml.etree.ElementTree as etree
import traceback
from datetime import datetime

import django.core.files as files

import superdesk.io.newsml as newsml
import superdesk.models as models

class Service(object):

    def __init__(self, session, storage):
        self.session = session
        self.storage = storage
        self.parser = newsml.Parser()

    def update(self):
        last_updated = models.Item.get_last_update()
        updated = datetime.utcnow()

        for channel in self.get_channels():
            for guid in self.get_ids(channel, last_updated, updated):
                items = self.get_items(guid)
                items.reverse()
                for item in items:
                    old = models.Item.objects(guid=item.guid).first()
                    if old and old.version < item.version:
                        old.delete()
                    elif old:
                        continue
                    self.fetch_assets(item)
                    item.save()

    def fetch_assets(self, item):
        for content in item.contents:
            if content.residRef and content.rendition in ['rend:viewImage']:
                name = self.storage.get_valid_name(content.residRef)
                if not self.storage.exists(name):
                    r = self.session.get(
                            content.href,
                            params={'token': self.get_token()})
                    tmp = files.temp.NamedTemporaryFile(delete=True)
                    tmp.write(r.content)
                    tmp.flush()
                    self.storage.save(name, files.File(tmp))

    def get_items(self, guid):
        """Parse item message and return given items."""
        payload = {'id': guid}
        tree = self.get_tree('item', payload)
        items = self.parser.parse_message(tree)
        return items

    def get_ids(self, channel, last_updated, updated):
        ids = []
        payload = {'channel': channel, 'fieldsRef': 'id'}
        payload['dateRange'] = "%s-%s" % (self.format_date(last_updated), self.format_date(updated))
        tree = self.get_tree('items', payload)
        for result in tree.findall('result'):
            ids.append(result.find('guid').text)
        return ids

    def get_channels(self):
        channels = []
        tree = self.get_tree('channels')
        for channel in tree.findall('channelInformation'):
            channels.append(channel.find('alias').text)
        return channels

    def get_tree(self, endpoint, payload=None):
        if payload is None:
            payload = {}
        payload['token'] = self.get_token()
        url = self.get_url(endpoint)
        response = self.session.get(url, params=payload)
        return etree.fromstring(response.text)

    def get_url(self, endpoint):
        return '/'.join(['http://rmb.reuters.com/rmd/rest/xml', endpoint])

    def get_token(self):
        if not hasattr(self, 'token'):
            self.token = get_token(self.session)
        return self.token

    def format_date(self, date):
        return date.strftime('%Y.%m.%d.%H.%M')

def get_token(session):
    """Get access token."""

    session.mount('https://', SSLAdapter())

    url = 'https://commerce.reuters.com/rmd/rest/xml/login'
    payload = {
            'username': os.environ.get('REUTERS_USERNAME', ''),
            'password': os.environ.get('REUTERS_PASSWORD', ''),
            }

    response = session.get(url, params=payload)
    tree = etree.fromstring(response.text)
    return tree.text

# workaround for ssl version error
class SSLAdapter(requests.adapters.HTTPAdapter):
    """SSL Adapter set for ssl tls v1."""

    def init_poolmanager(self, connections, maxsize):
        import ssl
        from requests.packages.urllib3.poolmanager import PoolManager
        self.poolmanager = PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                ssl_version = ssl.PROTOCOL_TLSv1)
