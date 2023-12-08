from django import forms

from Analytics.models import StatisticType, Statistic


class PlotForm(forms.Form):
    statistic_type = forms.ModelChoiceField(label='Statistic', queryset=StatisticType.objects.all(), required=True)
    eye = forms.ChoiceField(label='Eye', required=False, choices=((None, 'All'), ('L', 'Left'), ('R', 'Right')))
    rate = forms.CharField(widget=forms.HiddenInput(), required=False)
    statistic = forms.IntegerField(widget=forms.HiddenInput(), required=False)
