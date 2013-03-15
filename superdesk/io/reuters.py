"""Reuters io service."""

import os
import requests
import xml.etree.ElementTree as etree
import traceback
import datetime
import cloudinary.uploader

import superdesk.io.newsml as newsml
import superdesk.models as models

class Service(object):
    """Update Service"""

    URL = 'http://rmb.reuters.com/rmd/rest/xml'
    DATE_FORMAT = '%Y.%m.%d.%H.%M'

    def __init__(self):
        self.parser = newsml.Parser()
        self.token = get_token()

    def update(self):
        """Service update call."""

        updated = datetime.datetime.utcnow()
        last_updated = models.get_last_update()
        if not last_updated:
            last_updated = updated + datetime.timedelta(days=-1) # last 24h

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
        """Fetch remote assets for given item."""

        for content in item.contents:
            if content.residRef and content.rendition in ['rend:viewImage']:
                url = "%s?token=%s" % (content.href, self.token)
                status = cloudinary.uploader.upload(url,
                        public_id=content.residRef)
                content.storage = status['url']

    def get_items(self, guid):
        """Parse item message and return given items."""
        payload = {'id': guid}
        tree = self.get_tree('item', payload)
        items = self.parser.parse_message(tree)
        return items

    def get_ids(self, channel, last_updated, updated):
        """Get ids of documents which should be updated."""

        ids = []
        payload = {'channel': channel, 'fieldsRef': 'id'}
        payload['dateRange'] = "%s-%s" % (self.format_date(last_updated),
                self.format_date(updated))
        tree = self.get_tree('items', payload)
        for result in tree.findall('result'):
            ids.append(result.find('guid').text)
        return ids

    def get_channels(self):
        """Get subscribed channels."""

        channels = []
        tree = self.get_tree('channels')
        for channel in tree.findall('channelInformation'):
            channels.append(channel.find('alias').text)
        return channels

    def get_tree(self, endpoint, payload=None):
        """Get xml response for given API endpoint and payload."""

        if payload is None:
            payload = {}
        payload['token'] = self.token
        url = self.get_url(endpoint)

        try:
            response = requests.get(url, params=payload, timeout=5.0)
        except Exception as error:
            traceback.print_exc()
            print(url, payload)
            raise error

        try:
            return etree.fromstring(response.text.encode('utf-8'))
        except UnicodeEncodeError as error:
            print(response.text.encode('utf-8'))
            traceback.print_exc()
            raise error

    def get_url(self, endpoint):
        """Get API url for given endpoint."""
        return '/'.join([self.URL, endpoint])

    def format_date(self, date):
        """Format date for API usage."""
        return date.strftime(self.DATE_FORMAT)

def get_token():
    """Get access token."""

    session = requests.Session()
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
        """Init poolmanager to use ssl version v1."""

        import ssl
        from requests.packages.urllib3.poolmanager import PoolManager

        self.poolmanager = PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                ssl_version = ssl.PROTOCOL_TLSv1)
