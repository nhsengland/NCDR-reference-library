from .models import Version


def ncdr_latest_version(request):
    return {"ncdr_latest_version": Version.objects.latest()}
