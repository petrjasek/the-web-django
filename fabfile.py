from __future__ import unicode_literals
from fabric.api import *
from fabric.context_managers import shell_env

TEST_DATABASE = 'superdesk_test'

env.hosts = ['lab.sourcefabric.org']
env.port = 2209

def tdd():
    with shell_env(MONGOHQ_URL=TEST_DATABASE):
        local("nosetests")

def bdd():
    with shell_env(MONGOHQ_URL=TEST_DATABASE):
        local("./manage.py harvest")

def test():
    tdd()
    bdd()

def push():
    test()
    local("git push")

def runserver():
    local("./manage.py runserver")

def update():
    local("python3 manage.py updatereuters")

def rungunicorn():
    local("gunicorn_django -w 5")

def deploy():
    dest = '/home/petr/django/superdesk'

    with settings(warn_only=True):
        if run("test -d %s" % dest).failed:
            run("git clone git://github.com/petrjasek/the-web-django.git %s" % dest)

    with cd(dest):
        run("virtualenv env")
        run("git pull")
        with prefix("sh ./env/bin/activate"):
            run("./env/bin/pip install -r requirements.txt")
            run("./env/bin/python manage.py runserver &")

