from rest_framework import serializers
from csv_schema import models


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Column
        exclude = ('created', 'updated',)
