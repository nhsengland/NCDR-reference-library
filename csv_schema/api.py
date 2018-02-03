from rest_framework import viewsets
from csv_schema import models
from csv_schema import serializers
from rest_framework.routers import DefaultRouter


class DatabaseViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = models.Database.objects.all()
    serializer_class = serializers.DatabaseSerializer


router = DefaultRouter()
router.register(
    r'databases', DatabaseViewSet, base_name='database'
)
