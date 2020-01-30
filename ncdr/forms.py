from django import forms

from .models import Version


class UploadNcdrForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["db_structure", "definitions", "grouping_mapping"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["db_structure"].required = True
        self.fields["definitions"].required = True
        self.fields["grouping_mapping"].required = True


class UploadMetricsForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["metrics_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metrics_file"].required = True
