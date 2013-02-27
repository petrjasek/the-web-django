from lettuce import *
from lettuce.django import django_url
from django.test.client import Client
from bs4 import BeautifulSoup

@before.all
def set_browser():
    world.browser = Client()

@step(r'I send GET request to "(.*)"')
def access_url(step, url):
    world.response = world.browser.get(django_url(url))
    world.soup = BeautifulSoup(world.response.content)
    world.status_code = world.response.status_code
    world.title = world.soup.title.string
    world.articles = world.soup.find_all('article')

@step(r'I get response code ([1-5]\d\d)')
def test_response_code(step, code):
    expected = int(code)
    assert world.status_code == expected, "Got %d" % wold.status_code

@step(r'I see title "(.*)"')
def test_title(step, title):
    assert world.title == title, "Got %s" % world.title

@step(r'I see (\d+) articles?')
def test_article_count(step, count):
    expected = int(count)
    assert len(world.articles) == expected, "Got %d" % len(world.articles)
