from .models import Column


def unpublished_columns(request):
    return {"unpublished_columns": Column.objects.unpublished().count()}
