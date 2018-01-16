from django.conf import settings as s


def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return dict(settings=s)
