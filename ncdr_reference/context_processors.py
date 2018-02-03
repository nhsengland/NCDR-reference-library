from django.conf import settings as s
from django.utils.functional import SimpleLazyObject
from django.apps import apps


class ModelContextProcessor(object):
    def __init__(self):
        for i, v in apps.all_models.items():
            setattr(self, i, v)


def models(request):
    return {
        "models": SimpleLazyObject(ModelContextProcessor)
    }


def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return dict(settings=s)
