from dataclasses import fields
from msilib.schema import Class
from django import forms

from authentication.models import CustomUser
from core.models import NeighbourNote

# Rekvizitų įkėlimas
class UserTemplateHeader(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('template_header',)


