# summoner/forms.py

from django import forms

class SummonerSearchForm(forms.Form):
    riot_id = forms.CharField(label='Riot ID', max_length=50)
    tag_line = forms.CharField(label='Tag Line', max_length=50)
