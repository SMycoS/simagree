from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import *
import itertools
from django.db.models import Q

########## RECHERCHE ##########

class SearchForm(forms.Form):
    nomUsuel = forms.CharField(label = 'Nom', required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    genre = forms.CharField(label = 'Genre', required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    espece = forms.CharField(label = 'Espèce', required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    opts = [('all','Non renseigné'), ('yes', 'Oui'), ('no', 'Non')]
    comestible = forms.ChoiceField(label='Comestible', widget=forms.Select(attrs={'class' : 'form-control'}), choices=opts)
    presentSms = forms.BooleanField(label='Afficher uniquement les espèces présentes à la SMS', widget=forms.CheckboxInput(attrs={'class' : 'form-control'}), required=False)
    displaySyno = forms.BooleanField(label='Afficher les synonymes', widget=forms.CheckboxInput(attrs={'class' : 'form-control'}), required=False)
    a_imprimer = forms.BooleanField(label = 'A imprimer', widget=forms.CheckboxInput(attrs={'class' : 'form-control'}), required=False)

class LightSearchForm(forms.Form):
    genre = forms.CharField(label = 'Genre', required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    espece = forms.CharField(label = 'Espèce', required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))


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
            'biblio1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio3' : forms.TextInput(attrs={'class' : 'form-control'}),
        }

class AddFormId(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddFormId, self).__init__(*args, **kwargs)
        self.list = Themes.objects.all()
        self.fields['theme1'].queryset = self.list
        self.fields['theme1'].required = False
        self.fields['theme2'].queryset = self.list
        self.fields['theme2'].required = False
        self.fields['theme3'].queryset = self.list
        self.fields['theme3'].required = False
        self.fields['theme4'].queryset = self.list
        self.fields['theme4'].required = False
    
    def clean_comestible(self):
        form_com = self.cleaned_data.get("comestible")
        form_sms = self.cleaned_data.get("sms")
        if form_sms and (form_com == ""):
            raise forms.ValidationError(u"La comestibilité est obligatoire si le taxon est présent à la SMS")
        return form_com

    class Meta:
        model = Identifiants
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'noms' : forms.TextInput(attrs={'class' : 'form-control'}),
            'fiche' :forms.NumberInput(attrs={'class' : 'form-control'}),
            'sms' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
            'comestible' : forms.Select(attrs={'class' : 'form-control'}, choices = [(None, 'Inconnu'), ('C', 'Comestible'), ('NC', 'Non Comestible'), ('T', 'Toxique'), ('MO', 'Mortel')]),
            'a_imprimer' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
            'apparition' : forms.TextInput(attrs={'class' : 'form-control'}),
            'notes' : forms.Textarea(attrs={'class' : 'form-control'}),
            'ecologie' : forms.Textarea(attrs={'class' : 'form-control'}),
            'icono1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'icono3' : forms.TextInput(attrs={'class' : 'form-control'}),
            'theme1' : forms.Select(attrs={'class' : 'form-control'}),
            'theme2' : forms.Select(attrs={'class' : 'form-control'}),
            'theme3' : forms.Select(attrs={'class' : 'form-control'}),
            'theme4' : forms.Select(attrs={'class' : 'form-control'}),
        }

class AddFormPartial(forms.ModelForm):
    tax = forms.IntegerField(label = 'Taxon', widget=forms.NumberInput(attrs={'class' : 'form-control'}))

    def clean_tax(self):
        form_tax = self.cleaned_data.get("tax")

        existing = Nomenclature.objects.filter(
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
            'codesyno' : forms.Select(attrs={'class' : 'form-control'}, choices = [('0', 'VALIDE'), ('1', 'SYN'), ('3', 'SYN USUEL')]),
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

    def __init__(self, *args, **kwargs):
        super(ModForm, self).__init__(*args, **kwargs)
        self.fields['taxon'].disabled = True

    class Meta:
        model = Nomenclature
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'genre' : forms.TextInput(attrs={'class' : 'form-control'}),
            'espece' : forms.TextInput(attrs={'class' : 'form-control'}),
            'variete' : forms.TextInput(attrs={'class' : 'form-control'}),
            'forme' : forms.TextInput(attrs={'class' : 'form-control'}),
            'autorite' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio1' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio2' : forms.TextInput(attrs={'class' : 'form-control'}),
            'biblio3' : forms.TextInput(attrs={'class' : 'form-control'}),
            'codesyno' : forms.Select(attrs={'class' : 'form-control'}, choices = [('0', 'VALIDE'), ('1', 'SYN'), ('3', 'SYN USUEL')]),
        }

class ModFormTax(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModFormTax, self).__init__(*args, **kwargs)
        self.fields['taxon'].disabled = True
        self.fields['fiche'].disabled = True
        self.list = Themes.objects.all()
        self.fields['theme1'].queryset = self.list
        self.fields['theme1'].required = False
        self.fields['theme2'].queryset = self.list
        self.fields['theme2'].required = False
        self.fields['theme3'].queryset = self.list
        self.fields['theme3'].required = False
        self.fields['theme4'].queryset = self.list
        self.fields['theme4'].required = False
    
    def clean_comestible(self):
        form_com = self.cleaned_data.get("comestible")
        form_sms = self.cleaned_data.get("sms")
        if form_sms and (form_com == ""):
            raise forms.ValidationError(u"La comestibilité est obligatoire si le taxon est présent à la SMS")
        return form_com

    class Meta:
        model = Identifiants
        fields = '__all__'
        widgets = {
            'taxon' : forms.NumberInput(attrs={'class' : 'form-control'}),
            'noms' : forms.TextInput(attrs={'class' : 'form-control'}),
            'fiche' :forms.NumberInput(attrs={'class' : 'form-control'}),
            'sms' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
            'comestible' : forms.Select(attrs={'class' : 'form-control'}, choices = [(None, 'Inconnu'), ('C', 'Comestible'), ('NC', 'Non Comestible'), ('T', 'Toxique'), ('MO', 'Mortel')]),
            'a_imprimer' : forms.CheckboxInput(attrs={'class' : 'form-control'}),
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

        existing = Themes.objects.filter(
                       theme=form_theme
                   ).exists()
        if existing:
            raise forms.ValidationError(u"Le thème existe déjà")
        return form_theme

    class Meta:
        model = Themes
        fields = ['theme']
        widgets = {'theme' : forms.TextInput(attrs={'class' : 'form-control'})}


########## LISTES ##########

class AddListForm(forms.ModelForm):
    
    class Meta:
        model = ListeRecolte
        fields = '__all__'
        exclude = ('taxons'),
        widgets = {
            'date' : forms.DateInput(attrs={'class' : 'form-control', 'id' : 'datepicker'}),
        }

class AddLieuForm(forms.ModelForm):
    class Meta:
        model = LieuRecolte
        fields = '__all__'
        widgets = {
            'libelle' : forms.TextInput(attrs={'class' : 'form-control', 'id' : 'libelleInput'}),
            'commune' : forms.TextInput(attrs={'class' : 'form-control'}),
            'lieu_dit' : forms.TextInput(attrs={'class' : 'form-control'})
        }

        

class EditListTaxonsForm(forms.ModelForm):
    selectf = forms.MultipleChoiceField(widget = forms.SelectMultiple)
    class Meta:
        model = ListeRecolte
        fields = '__all__'
        exclude = ('taxons', )

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page')
        self.tax_list = kwargs.pop('taxons')
        super(EditListTaxonsForm, self).__init__(*args, **kwargs)

        self.offset = (self.page - 1) * 1000
        self.limit = self.offset + 1000
        self.fields['date'].disabled = True
        self.fields['lieu'].disabled = True
        
        self.init_choices = Nomenclature.objects.all().filter(Q(taxon__in = self.tax_list) & Q(codesyno = 0)).values(
            'taxon',
            'genre',
            'espece',
            'variete',
            'forme'
        )
        self.other_choices =  Nomenclature.objects.all().filter(~Q(taxon__in = self.tax_list)).values(
            'taxon',
            'genre',
            'espece',
            'variete',
            'forme'
            )[self.offset:self.limit]
        self.query = self.init_choices | self.other_choices
        self.opts = []
        self.inits = []
        
        for k in self.init_choices:
            self.inits.append(k['taxon'])
            self.opts.append((k['taxon'], str(k['taxon']) + ' - ' + k['genre'] + ' ' + k['espece'] + ' ( ' + k['variete'] + ' ' + k['forme'] + ' )'))
        for k in self.other_choices:
            self.opts.append((k['taxon'], str(k['taxon']) + ' - ' + k['genre'] + ' ' + k['espece'] + ' ( ' + k['variete'] + ' ' + k['forme'] + ' )'))
        self.initial['selectf'] = self.inits
        self.fields['selectf'].choices = self.opts    


class UploadFileForm(forms.Form):
    csv_id = forms.FileField(required = False)
    csv_nom = forms.FileField(required = False)
    csv_classification = forms.FileField(required = False)

