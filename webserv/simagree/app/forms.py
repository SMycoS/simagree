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

class AddFormNom(forms.ModelForm):
    class Meta:
        model = Nomenclature
        fields = '__all__'
        exclude = ('taxon'),

class AddFormId(forms.ModelForm):
    class Meta:
        model = Identifiants
        fields = '__all__'

class AddFormPartial(forms.ModelForm):
    tax = forms.IntegerField()

    def clean_tax(self):
        form_tax = self.cleaned_data.get("tax")

        existing = Nomenclature.objects.using('simagree').filter(
                       taxon_id=form_tax
                   ).exists()
        if not existing:
            raise forms.ValidationError(u"Le taxon n'existe pas")
        return form_tax
    class Meta:
        model = Nomenclature
        fields = '__all__'
        exclude = ('taxon'),