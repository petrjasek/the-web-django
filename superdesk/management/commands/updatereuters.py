"""
Reuters update command

"""

from __future__ import unicode_literals

import django.core.management.base as command

from superdesk.io import reuters

class Command(command.BaseCommand):
    """Update Reuters command."""

    help = 'Update Reuters Command'

    def handle(self, *args, **options):
        service = reuters.Service()
        service.update()
        return
