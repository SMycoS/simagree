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
        widgets = { 'codesyno' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'genre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'espece' : forms.TextInput(attrs={'class' : 'form-control'}),
            'variete' : forms.TextInput(attrs={'class' : 'form-control'}),
            'forme' : forms.TextInput(attrs={'class' : 'form-control'}),
            'autorite' : forms.TextInput(attrs={'class' : 'form-control'}),
            'moser' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio3' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

class AddFormId(forms.ModelForm):
    class Meta:
        model = Identifiants
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'noms' : forms.TextInput(attrs={'class' : 'form-control'}),
            'fiche' :forms.NumberInput(attrs={'class' : 'form-control'}),
            'comestible' : forms.TextInput(attrs={'class' : 'form-control'}),
            'sms' : forms.NullBooleanSelect(attrs={'class' : 'form-control'}),
            'a_imprimer' : forms.NullBooleanSelect(attrs={'class' : 'form-control'}),
            'lieu' : forms.TextInput(attrs={'class' : 'form-control'}),
            'apparition' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

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
        widgets = {
            'tax' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'codesyno' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'genre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'espece' : forms.TextInput(attrs={'class' : 'form-control'}),
            'variete' : forms.TextInput(attrs={'class' : 'form-control'}),
            'forme' : forms.TextInput(attrs={'class' : 'form-control'}),
            'autorite' : forms.TextInput(attrs={'class' : 'form-control'}),
            'moser' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio3' : forms.TextInput(attrs={'class' : 'form-control'}),

        }