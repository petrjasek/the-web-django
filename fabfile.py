from __future__ import unicode_literals
from fabric.api import local

def tdd():
    local("./manage.py test")

def bdd():
    local("./manage.py harvest")

def test():
    tdd()
    bdd()

def push():
    test()
    local("git push")

def runserver():
    local("./manage.py runserver")
