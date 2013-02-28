from lettuce import *
from lettuce.django import django_url
from django.test.client import Client
from django.conf import settings
from nose.tools import assert_equals
from bs4 import BeautifulSoup
import json
from superdesk.models import Item

@before.all
def set_browser():
    world.browser = Client()

@after.each_scenario
def drop_db(scenario):
    Item.drop_collection()

@step(r'Fixture "(.*)"')
def add_test_article(step, fixture):
    load_fixture(fixture)

@step(r'No fixture')
def no_fixture(step):
    pass

@step(r'I send request to "(.*)"')
def access_url(step, url):
    world.response = world.browser.get(django_url(url))
    world.soup = BeautifulSoup(world.response.content)

@step(r'I get response code ([1-5]\d\d)')
def test_response_code(step, code):
    assert_equals(int(code), world.response.status_code)

@step(r'I see title "(.*)"')
def test_title(step, title):
    assert_equals(title, world.soup.title.string)

@step(r'I see article links')
def test_article_count(step):
    articles = world.soup.find_all('article')
    assert_equals(3, len(articles))
    assert_equals(step.hashes[0]['title'], articles[0].a.string)

@step(r'I see link to "(.*)"')
def test_link_to(step, href):
    article = world.soup.article
    assert_equals("Bank cuts interest rates to record low", article.a.string)
    assert_equals(href, article.a['href'])

@step(r'I see h1 "(.*)"')
def test_h1(step, title):
    assert_equals(title, world.soup.h1.string)

@step(r'I see content with "(.*)"')
def test_content(step, content):
    assert world.soup.p.string.find(content)

def load_fixture(fixture):
    """load fixture from given file
    """
    with open('superdesk/fixtures/%s' % fixture) as fp:
        items = json.load(fp)
        for item_data in items:
            item = Item(**item_data)
            item.save(validate=False)
