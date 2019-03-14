from django import forms

from .models import Version


class UploadForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["db_structure", "definitions", "grouping_mapping"]
