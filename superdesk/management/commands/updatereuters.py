"""
Reuters update command

"""

from __future__ import unicode_literals
import requests

import django.core.files.storage as storages
import django.core.management.base as command

from superdesk.io import reuters

class Command(command.BaseCommand):
    """Update Reuters command."""

    help = 'Update Reuters Command'

    def handle(self, *args, **options):
        session = requests.Session()
        session.max_redirects = 3
        storage = storages.FileSystemStorage()
        service = reuters.Service(session, storage)
        service.update()
        return
