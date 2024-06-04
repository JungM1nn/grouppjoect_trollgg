from django import forms

class SummonerSearchForm(forms.Form):
    riot_id_tagline = forms.CharField(label='Riot ID # Tagline', max_length=100)
