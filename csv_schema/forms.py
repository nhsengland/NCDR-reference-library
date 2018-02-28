from django import forms
from csv_schema import models


class TableForm(forms.ModelForm):
    class Meta:
        model = models.Table
        fields = '__all__'
        widgets = {
            'is_table': forms.RadioSelect
        }


class DatabaseForm(forms.ModelForm):
    class Meta:
        model = models.Database
        fields = '__all__'


class ColumnForm(forms.ModelForm):
    class Meta:
        model = models.Column
        fields = '__all__'


class DataElementForm(forms.ModelForm):
    class Meta:
        model = models.DataElement
        fields = '__all__'


class GroupingForm(forms.ModelForm):
    class Meta:
        model = models.Grouping
        fields = '__all__'
