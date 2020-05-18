"""
Management command to check disk space on a server.
"""
import subprocess

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


def raise_the_alarm():
    body = " ".join(
        [
            "Routine system check on NCDR has detected a volume with > 90%",
            "disk usage. Please log in and investigate.",
        ]
    )
    send_mail(
        "NCDR Disk Space Alert: Action Required",
        body,
        settings.DEFAULT_FROM_EMAIL,
        [i[1] for i in settings.ADMINS],
    )


class Command(BaseCommand):
    def handle(self, *a, **k):
        p1 = subprocess.Popen(["df", "-h"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(
            ["awk", "{print $5}"], stdin=p1.stdout, stdout=subprocess.PIPE
        )
        p3 = subprocess.Popen(
            ["egrep", "9[0-9]%"], stdin=p2.stdout, stdout=subprocess.PIPE
        )
        out, er = p3.communicate()
        if out:
            raise_the_alarm()
        return
