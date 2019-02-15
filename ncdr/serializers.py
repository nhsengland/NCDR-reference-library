from rest_framework import serializers

from .models import Column


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        exclude = ("created", "updated")
