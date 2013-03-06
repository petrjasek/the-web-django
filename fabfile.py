from __future__ import unicode_literals
from fabric.api import local
from fabric.context_managers import shell_env

TEST_DATABASE = 'superdesk_test'

def tdd():
    with shell_env(SUPERDESK_DATABASE=TEST_DATABASE):
        local("nosetests")

def bdd():
    with shell_env(SUPERDESK_DATABASE=TEST_DATABASE):
        local("./manage.py harvest")

def test():
    tdd()
    bdd()

def push():
    test()
    local("git push")

def runserver():
    local("./manage.py runserver")
