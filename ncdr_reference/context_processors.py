from django.conf import settings as s
from django.utils.functional import SimpleLazyObject
from django.apps import apps


class ModelContextProcessor(object):
    def __init__(self):
        for i, v in apps.all_models.items():
            setattr(self, i, v)


class ModelObjectContextProcessor(object):
    def __init__(self):
        for i, v in apps.all_models.items():
            result = {}
            for model_name, model in v.items():
                result[model_name] = model.objects
            setattr(self, i, result)


def models(request):
    result = {
        "models": SimpleLazyObject(ModelContextProcessor),
        "model_objects": SimpleLazyObject(ModelObjectContextProcessor)
    }
    return result


def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return dict(settings=s)
