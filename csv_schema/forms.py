from django import forms
from csv_schema import models
from django.utils.html import (
    mark_safe, format_html, escape
)
from django.forms.utils import flatatt


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


class GroupedModelChoiceField(forms.ModelChoiceField):

    def optgroup_from_instance(self, obj):
        return ""

    def __choice_from_instance__(self, obj):
        return (obj.id, self.label_from_instance(obj))

    def _get_choices(self):
        if not self.queryset:
            return []

        all_choices = []
        if self.empty_label:
            current_optgroup = ""
            current_optgroup_choices = [("", self.empty_label)]
        else:
            current_optgroup = self.optgroup_from_instance(self.queryset[0])
            current_optgroup_choices = []

        for item in self.queryset:
            optgroup_from_instance = self.optgroup_from_instance(item)
            if current_optgroup != optgroup_from_instance:
                all_choices.append((current_optgroup, current_optgroup_choices))
                current_optgroup_choices = []
                current_optgroup = optgroup_from_instance
            current_optgroup_choices.append(self.__choice_from_instance__(item))

        all_choices.append((current_optgroup, current_optgroup_choices))
        return all_choices

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class ColumnSelectField(GroupedModelChoiceField):
    def optgroup_from_instance(self, obj):
        return obj.database.name


class CreateColumnForm(forms.ModelForm):
    class Meta:
        model = models.Column
        exclude = ['slug']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table'].label = "Which Table Would You Like to Add Columns To"

    table = ColumnSelectField(
        queryset=models.Table.objects.all().order_by("database__name")
    )


class ColumnForm(forms.ModelForm):
    class Meta:
        model = models.Column
        exclude = ['slug']

    table = ColumnSelectField(
        queryset=models.Table.objects.all()
    )


class DataElementForm(forms.ModelForm):
    class Meta:
        model = models.DataElement
        fields = '__all__'


class GroupingForm(forms.ModelForm):
    class Meta:
        model = models.Grouping
        exclude = ['slug']
