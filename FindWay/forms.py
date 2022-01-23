from django import forms

class WayForm(forms.Form):
    start = forms.CharField(label='Start', max_length=100)
    end = forms.CharField(label='End', max_length=100)