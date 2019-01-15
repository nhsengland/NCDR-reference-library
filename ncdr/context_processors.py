from django.apps import apps
from django.conf import settings as s
from django.utils.functional import SimpleLazyObject


class ModelContextProcessor(object):
    def __init__(self):
        for i, v in apps.all_models.items():
            setattr(self, i, v)


class ModelObjectsContextProcessor(object):
    def __init__(self):
        for i, v in apps.all_models.items():
            setattr(self, i, {k: y.objects for k, y in v.items()})


def models(request):
    return {
        "models": SimpleLazyObject(ModelContextProcessor),
        "model_objects": SimpleLazyObject(ModelObjectsContextProcessor)
    }


def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return dict(settings=s)
