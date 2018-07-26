from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import *

########## RECHERCHE ##########

class SearchForm(forms.Form):
    nomUsuel = forms.CharField(label = 'Nom', required=False)
    genre = forms.CharField(label = 'Genre', required=False)
    espece = forms.CharField(label = 'Espèce', required=False)
    opts = [('all','Non renseigné'), ('yes', 'Oui'), ('no', 'Non')]
    comestible = forms.ChoiceField(label='Comestible', widget=forms.Select, choices=opts)
    presentSms = forms.BooleanField(label='Afficher uniquement les espèces présentes à la SMS', widget=forms.CheckboxInput, required=False)
    displaySyno = forms.BooleanField(label='Afficher les synonymes', widget=forms.CheckboxInput, required=False)


########## AJOUT ##########

class AddFormNom(forms.ModelForm):

    class Meta:
        model = Nomenclature
        fields = '__all__'
        exclude = ['taxon','codesyno']
        widgets = {
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

    def __init__(self, *args, **kwargs):
        super(AddFormId, self).__init__(*args, **kwargs)
        self.list = Themes.objects.using('simagree').all()
        self.fields['theme1'].queryset = self.list
        self.fields['theme1'].required = False
        self.fields['theme2'].queryset = self.list
        self.fields['theme2'].required = False
        self.fields['theme3'].queryset = self.list
        self.fields['theme3'].required = False
        self.fields['theme4'].queryset = self.list
        self.fields['theme4'].required = False

    class Meta:
        model = Identifiants
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'noms' : forms.TextInput(attrs={'class' : 'form-control'}),
            'fiche' :forms.NumberInput(attrs={'class' : 'form-control'}),
            'comestible' : forms.TextInput(attrs={'class' : 'form-control'}),
            'sms' : forms.NullBooleanSelect(attrs={'class' : 'form-control'}),
            'a_imprimer' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
            'lieu' : forms.TextInput(attrs={'class' : 'form-control'}),
            'apparition' : forms.TextInput(attrs={'class' : 'form-control'}),
            'notes' : forms.Textarea(attrs={'class' : 'form-control'}),
            'ecologie' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono3' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

class AddFormPartial(forms.ModelForm):
    tax = forms.IntegerField(label = 'Taxon', widget=forms.NumberInput(attrs={'class' : 'form-control'}))

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

class ModForm(forms.ModelForm):
    class Meta:
        model = Nomenclature
        fields = '__all__'
        exclude = ('taxon'),
        widgets = {
            'genre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'espece' : forms.TextInput(attrs={'class' : 'form-control'}),
            'variete' : forms.TextInput(attrs={'class' : 'form-control'}),
            'forme' : forms.TextInput(attrs={'class' : 'form-control'}),
            'autorite' : forms.TextInput(attrs={'class' : 'form-control'}),
            'moser' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio3' : forms.TextInput(attrs={'class' : 'form-control'}),
            'codesyno' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

class ModFormTax(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModFormTax, self).__init__(*args, **kwargs)
        self.fields['taxon'].disabled = True
        self.fields['fiche'].disabled = True
        self.list = Themes.objects.using('simagree').all()
        self.fields['theme1'].queryset = self.list
        self.fields['theme1'].required = False
        self.fields['theme2'].queryset = self.list
        self.fields['theme2'].required = False
        self.fields['theme3'].queryset = self.list
        self.fields['theme3'].required = False
        self.fields['theme4'].queryset = self.list
        self.fields['theme4'].required = False

    class Meta:
        model = Identifiants
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'noms' : forms.TextInput(attrs={'class' : 'form-control'}),
            'fiche' :forms.NumberInput(attrs={'class' : 'form-control'}),
            'comestible' : forms.TextInput(attrs={'class' : 'form-control'}),
            'sms' : forms.NullBooleanSelect(attrs={'class' : 'form-control'}),
            'a_imprimer' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
            'lieu' : forms.TextInput(attrs={'class' : 'form-control'}),
            'apparition' : forms.TextInput(attrs={'class' : 'form-control'}),
            'notes' : forms.Textarea(attrs={'class' : 'form-control'}),
            'ecologie' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono3' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

########## CONNEXION ##########

class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=30, widget = forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-control', 'placeholder' : "Mot de passe"}))


########## THEMES ##########

class AddThemeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs): 
        super(AddThemeForm, self).__init__(*args, **kwargs)
        self.fields['theme'].label = ""
        self.fields['theme'].help_text = ""
    def clean_theme(self):
        form_theme = self.cleaned_data.get("theme")

        existing = Themes.objects.using('simagree').filter(
                       theme=form_theme
                   ).exists()
        if existing:
            raise forms.ValidationError(u"Le thème existe déjà")
        return form_theme

    class Meta:
        model = Themes
        fields = '__all__'
        widgets = {'theme' : forms.TextInput(attrs={'class' : 'form-control'})}


########## LISTES ##########

class AddListForm(forms.ModelForm):
    opts = [('1', 'Opt 1'), ('2', 'Opt 2'), ('3', 'Opt 3')]
    selectf = forms.MultipleChoiceField(label = '', widget=forms.SelectMultiple(attrs={'class' : 'form-control'}), choices = opts)
    class Meta:
        model = ListeRecolte
        fields = '__all__'
        exclude = ('taxons'),
        widgets = {
            'date' : forms.DateInput(attrs={'class' : 'form-control', 'id' : 'datepicker'}),
            'lieu' : forms.TextInput(attrs={'class' : 'form-control'})
        }