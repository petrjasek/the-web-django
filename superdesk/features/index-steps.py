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

@step(r'I get response code ([1-5][0-9]{2})')
def test_response_code(step, code):
    assert world.response.status_code == int(code)

@step(r'I see title "(.*)"')
def test_title(step, title):
    assert world.soup.title.string == title

@step(r'I see ([0-9]+) article')
def test_article_count(step, count):
    assert len(world.soup.find_all('article')) == int(count)
