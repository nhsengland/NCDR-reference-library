from .models import Version
from django.conf import settings as project_settings


def latest_version(request):
    return {"latest_version": Version.objects.latest()}


def settings(request):
    return {"settings": project_settings}
