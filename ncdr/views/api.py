from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from ..models import Column
from ..serializers import ColumnSerializer


class ColumnViewSet(viewsets.ModelViewSet):
    base_name = "columns"
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


router = DefaultRouter()
router.register(ColumnViewSet.base_name, ColumnViewSet, ColumnViewSet.base_name)
