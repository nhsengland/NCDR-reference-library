from .models import Version


def latest_version(request):
    return {"latest_version": Version.objects.latest()}
