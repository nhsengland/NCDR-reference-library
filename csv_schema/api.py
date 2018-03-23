from rest_framework import mixins, viewsets
from csv_schema import models
from csv_schema import serializers
from rest_framework.routers import DefaultRouter


class ColumnViewSet(
    viewsets.ModelViewSet
):
    base_name = "columns"
    queryset = models.Column.objects.all()
    serializer_class = serializers.ColumnSerializer


router = DefaultRouter()
router.register(
    ColumnViewSet.base_name, ColumnViewSet, ColumnViewSet.base_name
)
