from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import *

class SearchForm(forms.Form):
    nomUsuel = forms.CharField(label = 'Nom', required=False)
    genre = forms.CharField(label = 'Genre', required=False)
    espece = forms.CharField(label = 'Espèce', required=False)
    opts = [('all','Non renseigné'), ('yes', 'Oui'), ('no', 'Non')]
    comestible = forms.ChoiceField(label='Comestible', widget=forms.Select, choices=opts)
    presentSms = forms.BooleanField(label='Afficher uniquement les espèces présentes à la SMS', widget=forms.CheckboxInput, required=False)
    displaySyno = forms.BooleanField(label='Afficher les synonymes', widget=forms.CheckboxInput, required=False)

class AddForm(forms.Form):
    taxon = forms.IntegerField(label = 'Taxon')
    genre = forms.CharField(label = 'Genre')
    espece = forms.CharField(label = 'Espèce')
    noms = forms.CharField(label = 'Noms usuels')
    opts = [('','Non renseigné'), ('C', 'Comestible'), ('NC', 'Non comestible'), ('T', 'Toxique'), ('M', 'Mortel')]
    comestible = forms.ChoiceField(label='Comestible', widget=forms.Select, choices=opts)
    presentSms = forms.BooleanField(label='Présent à la SMS', widget=forms.CheckboxInput, required=False)
    codeSyno = forms.IntegerField(label = 'Code synonyme')
    forme = forms.CharField(label = 'Forme')
    variete = forms.CharField(label = 'Variété')
    eco = forms.CharField(label = 'Ecologie')
    notes = forms.CharField(label = 'Notes', widget=forms.Textarea)

class MyModelForm(forms.ModelForm):
    class Meta:
        model = Nomenclature
        fields = '__all__'
        exclude = ('taxon'),

class MyMod(forms.ModelForm):
    class Meta:
        model = Identifiants
        fields = '__all__'
