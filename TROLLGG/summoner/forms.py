# forms.py
from django import forms

class SummonerSearchForm(forms.Form):
    riot_id_tagline = forms.CharField(label='Riot ID#Tag Line', max_length=50)
