from rest_framework import serializers
from csv_schema import models


class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Database
        fields = (
            "id", "name", "description", "link",
        )
