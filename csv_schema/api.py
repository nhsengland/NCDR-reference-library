from rest_framework import viewsets
from csv_schema import models
from csv_schema import serializers
from rest_framework.routers import DefaultRouter


class DatabaseViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing databases.
    """
    queryset = models.Database.objects.all()
    serializer_class = serializers.DatabaseSerializer


class TableViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing tables.
    """
    queryset = models.Table.objects.all()
    serializer_class = serializers.TableSerializer


class GroupingViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing groupings.
    """
    queryset = models.Grouping.objects.all()
    serializer_class = serializers.GroupingSerializer


class ColumnViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing groupings.
    """
    queryset = models.Column.objects.all()
    serializer_class = serializers.ColumnSerializer


router = DefaultRouter()

router.register(
    r'database', DatabaseViewSet, base_name='database',
)
router.register(
    r'table', TableViewSet, base_name='table'
)
router.register(
    r'grouping', GroupingViewSet, base_name='grouping'
)
router.register(
    r'column', ColumnViewSet, base_name='column'
)
