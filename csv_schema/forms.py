from django.forms import ModelForm
from csv_schema import models


class TableForm(ModelForm):
    class Meta:
        model = models.Table
        fields = '__all__'


class DatabaseForm(ModelForm):
    class Meta:
        model = models.Database
        fields = '__all__'


class ColumnForm(ModelForm):
    class Meta:
        model = models.Column
        fields = '__all__'


class DataElementForm(ModelForm):
    class Meta:
        model = models.DataElement
        fields = '__all__'


class GroupingForm(ModelForm):
    class Meta:
        model = models.Grouping
        fields = '__all__'
