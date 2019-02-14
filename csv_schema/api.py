from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from csv_schema import models, serializers


class ColumnViewSet(viewsets.ModelViewSet):
    base_name = "columns"
    queryset = models.Column.objects.all()
    serializer_class = serializers.ColumnSerializer


router = DefaultRouter()
router.register(ColumnViewSet.base_name, ColumnViewSet, ColumnViewSet.base_name)
