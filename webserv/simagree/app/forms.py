from django import forms

class SearchForm(forms.Form):
    nomUsuel = forms.CharField(label = 'Nom', required=False)
    genre = forms.CharField(label = 'Genre', required=False)
    espece = forms.CharField(label = 'Espèce', required=False)
    opts = [('all','Non renseigné'), ('yes', 'Oui'), ('no', 'Non')]
    comestible = forms.ChoiceField(label='Comestible', widget=forms.Select, choices=opts)
    presentSms = forms.BooleanField(label='Afficher uniquement les espèces présentes à la SMS', widget=forms.CheckboxInput, required=False)
    displaySyno = forms.BooleanField(label='Afficher les synonymes', widget=forms.CheckboxInput, required=False)

