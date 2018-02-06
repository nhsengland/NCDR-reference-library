from rest_framework import serializers
from csv_schema import models


class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Database
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Table
        fields = "__all__"


class GroupingSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    class Meta:
        model = models.Grouping
        fields = "__all__"


class ColumnSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    class Meta:
        model = models.Column
        fields = "__all__"
