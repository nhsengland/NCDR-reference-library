from django import forms

from .models import Column, Database, DataElement, Grouping, Table


class ColumnSelectField(forms.ModelChoiceField):
    def optgroup_from_instance(self, obj):
        return obj.schema.database.name

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


class CreateColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = [
            "name",
            "description",
            "data_type",
            "derivation",
            "data_element",
            "table",
            "technical_check",
            "is_derived_item",
            "definition_id",
            "author",
            "created_date_ext",
            "link",
            # "published",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        databases = Database.objects.order_by("name")
        self.fields["database"] = forms.ModelChoiceField(queryset=databases)
        self.fields["database"].label = "Select a Database"

        self.fields["table"] = ColumnSelectField(queryset=Table.objects.none())
        self.fields["table"].label = "Which Table Would You Like to Add Columns To"


class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = [
            "name",
            "description",
            "data_type",
            "derivation",
            "data_element",
            "table",
            "technical_check",
            "is_derived_item",
            "definition_id",
            "author",
            "created_date_ext",
            "link",
            # "published",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["table"] = ColumnSelectField(queryset=Table.objects.all())


class DatabaseForm(forms.ModelForm):
    class Meta:
        model = Database
        fields = "__all__"


class DataElementForm(forms.ModelForm):
    class Meta:
        model = DataElement
        fields = "__all__"


class GroupingForm(forms.ModelForm):
    class Meta:
        model = Grouping
        exclude = ["slug"]


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = "__all__"
        widgets = {"is_table": forms.RadioSelect}
