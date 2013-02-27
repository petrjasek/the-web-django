from __future__ import unicode_literals
from fabric.api import local

def test():
    local("./manage.py test")
    local("./manage.py harvest")

def push():
    test()
    local("git push")

def runserver():
    local("./manage.py runserver")
