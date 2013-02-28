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

@step(r'I send GET request to "(.*)"')
def access_url(step, url):
    world.response = world.browser.get(django_url(url))
    world.soup = BeautifulSoup(world.response.content)
    world.status_code = world.response.status_code
    world.title = world.soup.title.string

@step(r'I get response code ([1-5]\d\d)')
def test_response_code(step, code):
    assert_equals(int(code), world.status_code)

@step(r'I see title "(.*)"')
def test_title(step, title):
    assert_equals(title, world.title)

@step(r'I see (\d) section with title "(.*)"')
def test_section_title(step, count, title):
    sections = world.soup.find_all('section')
    assert_equals(int(count), len(sections))
    assert_equals(title, sections[0].h1.string)

@step(r'I see (\d) articles')
def test_article_count(step, count):
    articles = world.soup.find_all('article')
    assert_equals(int(count), len(articles))
    assert_equals("Bank cuts interest rates to record low", articles[0].a.string)

def load_fixture(fixture):
    """load fixture from given file
    """
    with open('superdesk/fixtures/%s' % fixture) as fp:
        data = json.load(fp)
        item = Item(**data)
        item.save(validate=False)
