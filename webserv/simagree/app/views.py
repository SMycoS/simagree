from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.db.models import Q
from django.core import serializers
from wsgiref.util import FileWrapper
from django.template import Context, loader

import os
import datetime
import csv
import traceback
from io import StringIO



# Create your views here.

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest, light_dbRequest
from .pdfgen import *
from .csvparser import *

### Divers ###

req_size = 500 # nombre d'objets par requête de recherche

def none2string(s):
    if s is None:
        return ''
    else:
        return str(s)

########## Vues pour la connexion ##########

def accueil(req):
    return render(req, 'home.html')

def connexion(request):
    error = False
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur
            else: # sinon une erreur sera affichée
                error = True
            return redirect(reverse(accueil))
    else:
        form = ConnexionForm()

    return render(request, 'login.html', locals())

def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))

# Redirection pour les utilisateurs non authentifiés

########## Vues générales ##########


def search(req):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    # if this is a POST request we need to process the form data
    if req.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(req.GET or None, auto_id=True)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            items = dbRequest(form.cleaned_data, (req_size, int(req.GET['page'])))
            return render(req, 'search.html', {
                'form' : form,
                'shrooms' : items[1],
                'total' : items[0],
                'pages' : range(items[0] // req_size),
                'pages_int' : items[0] // req_size
                })
    else:
        form = SearchForm(auto_id=True)

    return render(req, 'search.html',{'form' : form})


########## Vues pour la gestion des champignons ##########

def add(req):
    if req.user.is_authenticated:
        # récupération de l'ensemble des taxons
        # première requête
        if req.method == 'GET':
            id_form = AddFormId(req.GET or None)
            nom_form = AddFormNom(req.GET or None)
            search_form = LightSearchForm()
        # après envoi du formulaire
        elif req.method == 'POST' and req.POST['action'] == "add":
            id_form = AddFormId(req.POST)
            nom_form = AddFormNom(req.POST)
            search_form = LightSearchForm(req.POST)
            if id_form.is_valid():
                print('id ok')
            if nom_form.is_valid():
                print('nom ok')
            else:
                print(nom_form.errors)
                print(nom_form)
            if id_form.is_valid() and nom_form.is_valid():
                print('valid')
                # sauvegarde dans la table Identifiants
                inst = id_form.save(commit = False)
                inst.save(using='simagree')
                # sauvegarde dans la table Nomenclature
                values = nom_form.save(commit = False)
                values.taxon = inst
                values.codesyno = 0
                values.save(using='simagree')
                return redirect(reverse(details, kwargs = {'id_item' : values.id}))
        # Recherche
        else:
            id_form = AddFormId()
            nom_form = AddFormNom()
            search_form = LightSearchForm(req.POST)
            if search_form.is_valid():
                items = light_dbRequest(search_form.cleaned_data)
                return render(req, 'add.html', {
                    'form' : id_form, 
                    'form2' : nom_form,
                    'searchform' : search_form, 
                    'results':items
                    })
        return render(req, 'add.html', {'form' : id_form, 'form2' : nom_form,'searchform' : search_form})
    else:
        return redirect(reverse(connexion))


def addPartial(req):
    if req.user.is_authenticated:
        if req.method == 'GET':
            nom_form = AddFormPartial(req.GET or None)
            search_form = LightSearchForm()
        elif req.method == 'POST' and req.POST['action'] == "add":
            nom_form = AddFormPartial(req.POST)
            search_form = LightSearchForm(req.POST)
            if nom_form.is_valid():
                id = nom_form.cleaned_data['tax']
                inst = Identifiants.objects.using('simagree').get(taxon = id)
                values = nom_form.save(commit = False)
                values.taxon = inst
                # vérification du code synonyme
                if values.codesyno == 0:
                    Nomenclature.objects.using('simagree').filter(Q(taxon=inst.taxon) & Q(codesyno=0)).update(codesyno=1)
                values.save(using='simagree')
                return redirect(reverse(details, kwargs = {'id_item' : values.id}))
        else:
            nom_form = AddFormPartial()
            search_form = LightSearchForm(req.POST)
            if search_form.is_valid():
                items = light_dbRequest(search_form.cleaned_data)
                return render(req, 'add_partial.html', {
                    'form' : nom_form,
                    'searchform' : search_form, 
                    'results':items
                    })
        
        return render(req, 'add_partial.html', {'form' : nom_form, 'searchform' : search_form})
    
    
    else:
        return redirect(reverse(connexion))

def details(req, id_item):
    if req.user.is_authenticated:
        item = Nomenclature.objects.using('simagree').select_related('taxon').filter(id = id_item).values(
            'taxon_id', 
            'taxon__noms', 
            'taxon__comestible', 
            'taxon__sms',
            'taxon__theme1',
            'taxon__theme2',
            'taxon__theme3',
            'taxon__theme4',
            'taxon__fiche',
            'taxon__apparition',
            'taxon__notes',
            'taxon__ecologie',
            'taxon__icono1',
            'taxon__icono2',
            'taxon__icono3',
            'taxon__num_herbier',
            'codesyno', 
            'genre', 
            'espece', 
            'variete', 
            'forme',
            'autorite',
            'biblio1',
            'biblio2',
            'biblio3',
            'moser',
            'date'
            )[0]
        try:    
            item['taxon__noms'] = item['taxon__noms'].splitlines()
        except:
            pass
        try:
            others = Nomenclature.objects.using('simagree').filter(Q(taxon = item['taxon_id']) & ~Q(id = id_item)).values('genre', 'espece', 'id', 'codesyno', 'variete', 'autorite')
            return render(req, 'details.html', {'shroom' : item, 'others' : others})
        except:
            return render(req, 'details.html', {'shroom' : item})
    else:
        return redirect(reverse(connexion))

def deleteConfirm(req):
    if req.method == 'POST':
        item = Nomenclature.objects.using('simagree').get(id = req.POST.get('ident'))
        item.delete()
        return HttpResponseRedirect(req.POST.get('next'))

def deleteTaxon(req):
    if req.method == 'POST':
        item = Identifiants.objects.using('simagree').get(taxon = req.POST.get('taxon'))
        item.delete()
        return HttpResponseRedirect(req.POST.get('next'))

def modify(req, id):
    if req.user.is_authenticated:
        inst_nom = Nomenclature.objects.using('simagree').get(id = id)
        # première requête
        if req.method == 'GET':
            nom_form = ModForm(req.GET or None, instance=inst_nom)
        # après envoi du formulaire
        elif req.method == 'POST':
            nom_form = ModForm(req.POST, instance = inst_nom)
            if nom_form.is_valid():
                # sauvegarde dans la table Nomenclature
                values = nom_form.save(commit = False)
                # vérification du code synonyme
                if values.codesyno == 0:
                    Nomenclature.objects.using('simagree').filter(Q(taxon=values.taxon) & Q(codesyno=0)).update(codesyno=1)
                values.save(using='simagree')

        return render(req, 'modify.html', {'form' : nom_form})
    else:
        return redirect(reverse(connexion))

def modifyTaxon(req, tax):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    inst = Identifiants.objects.using('simagree').get(taxon = tax)
    if req.method == 'GET':
        form = ModFormTax(req.GET or None, instance = inst)
    elif req.method == 'POST':
        form = ModFormTax(req.POST, instance = inst)
        if form.is_valid():
            values = form.save(commit = False)
            values.save()
    return render(req, 'modify_tax.html', {'form' : form})




########## Vues pour la gestion des thèmes ##########

def themes(req):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    themes_list = Themes.objects.using('simagree').all()
    if req.method == 'GET':
        form = AddThemeForm(req.GET or None)
    elif req.method == 'POST':
        form = AddThemeForm(req.POST)
        if form.is_valid():
            inst = form.save(commit = False)
            inst.save(using='simagree')
    return render(req, 'add_theme.html', {'form' : form, 'themes_list' : themes_list})

def deleteTheme(req):
    if req.method == 'POST':
        item = Themes.objects.using('simagree').get(id = req.POST.get('ident'))
        item.delete()
        return redirect(reverse(themes))


########## Vues pour la gestion des pdf ##########

def send_file(request, tax, type):

    #Suppression des fiches si trop nombreuses dans le dossier
    files = next(os.walk('./app/pdf_assets/fiches'))[2]
    if len(files) > 100:
        for i in files:
            os.remove('./app/pdf_assets/fiches/' + i)

    # Generation du pdf
    item = Nomenclature.objects.using('simagree').select_related('taxon').filter(Q(taxon = tax) & Q(codesyno = 0)).values(
        'taxon__theme1',
        'taxon__fiche',
        'genre',
        'espece',
        'variete',
        'taxon__noms',
        'forme' ,
        'taxon__comestible',
    )[0]
    vars = {}

    try:
        vars['theme'] = none2string(item['taxon__theme1'])
        vars['fiche'] = none2string(item['taxon__fiche'])
        vars['genre'] = item['genre']
        vars['espece'] = item['espece']
        vars['variete'] = none2string(item['variete'])
        vars['forme'] = none2string(item['forme'])
        vars['noms'] = none2string(item['taxon__noms'])
        vars['comestibilite'] = none2string(item['taxon__comestible'])
        vars['obs'] = "C'est joli"
        fullpath = 'app/pdf_assets/fiches/' + none2string(item['taxon__fiche']) + '.pdf'
    except Exception as e:
        raise Http404()
    try:
        if type == "theme":
            generateFicheTheme(fullpath, vars)
        else:
            generateFiche(fullpath, vars)
        return FileResponse(open(fullpath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

########## Vues pour la gestion des fiches récolte ##########

def editList(req, id_liste):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    liste_instance = ListeRecolte.objects.get(id = id_liste)
    opts = Nomenclature.objects.all()[:500]
    current_items = liste_instance.initia
    if req.method == "POST" and req.POST['action'] == "search":
        searchform = LightSearchForm(req.POST)
        listeform = EditListTaxonsForm(instance = liste_instance)
        if searchform.is_valid():
            results = light_dbRequest_bis(searchform.cleaned_data, (req_size, 1))
    elif req.method == "POST" and req.POST['action'] == "edit":
        searchform = LightSearchForm()
        listeform = EditListTaxonsForm(instance=liste_instance)
        if listeform.is_valid():
            print('oui')
    else:
        searchform = LightSearchForm()
        listeform = EditListTaxonsForm(instance = liste_instance, base=opts, initial={'selectf': current_items})
    return render(req, 'listes_create.html', {
        'searchform' : searchform, 
        'listeform' : listeform,
        })

def showLists(req):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    listes = ListeRecolte.objects.using('simagree').all().only('lieu', 'date', 'id')
    lieux = LieuRecolte.objects.using('simagree').all()
    modal_display = ''
    if req.method == "POST" and req.POST['action'] == "lieu":
        liste_form = AddListForm()
        lieu_form = AddLieuForm(req.POST)
        modal_display = "lieu"
        if lieu_form.is_valid():
            lieu_form.save()
    elif req.method == "POST" and req.POST['action'] == "liste":
        liste_form = AddListForm(req.POST)
        lieu_form = AddLieuForm()
        modal_display = "liste"
        if liste_form.is_valid():
            liste_form.save()
    elif req.method == "POST" and req.POST['action'] == "deleteLieu":
        liste_form = AddListForm()
        lieu_form = AddLieuForm()
        lieu = LieuRecolte.objects.get(id = req.POST['ident'])
        lieu.delete()
    else:
        liste_form = AddListForm()
        lieu_form = AddLieuForm()

    return render(req, 'listes.html', {
        'listes' : listes,
        'lieux' : lieux,
        'listeform' : liste_form,
        'lieuform' : lieu_form,
        'modal_display' : modal_display
        })

def detailsList(req, id_liste):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    liste = ListeRecolte.objects.using('simagree').get(id = id_liste)
    taxons = []
    for i in liste.taxons.all():
        if (int(i.taxon) not in taxons):
            taxons.append(int(i.taxon))
    items = Nomenclature.objects.using('simagree').select_related('taxon').filter(Q(taxon__in = taxons) & Q(codesyno = 0)).values('genre', 'espece')
    return render(req, 'listes.html', {'liste' : liste, 'items' : items})

def modList(req, id_liste):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    liste = ListeRecolte.objects.using('simagree').get(id = id_liste)
    all_taxons = Nomenclature.objects.using('simagree').select_related('taxon').only('taxon_id', 'genre', 'espece')
    if req.method == "POST":
        form = AddListForm(req.POST, instance = liste)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = AddListForm(instance = liste)


########## Vues pour l'import / export de la base en csv ##########

def csvIdent(req):
    # Création d'une reponse au format csv
    response = HttpResponse(content_type='text/csv')
    filename = datetime.datetime.now().strftime('"SMS_Identifiants_%d-%m-%Y.csv"')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    # Création du header
    csv_header = (
        'Taxon',
        'Noms usuels',
        'Fiche',
        'Comestibilité',
        'SMS',
        'A imprimer',
        'Lieu',
        'Apparition',
        'Notes',
        'Ecologie',
        'Thème 1',
        'Thème 2',
        'Thème 3',
        'Thème 4',
        'Iconographie 1',
        'Iconographie 2',
        'Iconographie 3',
        'Numéro herbier'
    )
    # Chargement du fichier templace
    template = loader.get_template('csv_identifiants_template.txt')

    # Objet
    c = {
        'header' : csv_header,
        'data' : Identifiants.objects.using('simagree').all()
    }
    response.write(template.render(c))
    return response

def csvNomenc(req):
    # Création d'une reponse au format csv
    response = HttpResponse(content_type='text/csv')    
    filename = datetime.datetime.now().strftime('"SMS_Nomenclature_%d-%m-%Y.csv"')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    # Création du header
    csv_header = (
        'Taxon',
        'Code Synonyme',
        'Genre',
        'Espèce',
        'Variété',
        'Forme',
        'Autorité',
        'Biliographie 1',
        'Bibliographie 2',
        'Bibliographie 3',
        'Tri MOSER',
        'Date'
    )
    # Chargement du fichier templace
    template = loader.get_template('csv_nomenclature_template.txt')

    # Objet
    c = {
        'header' : csv_header,
        'data' : Nomenclature.objects.using('simagree').all().order_by('taxon_id', 'codesyno')
    }
    response.write(template.render(c))
    return response
    

def upload_csv(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    if "GET" == request.method:
        form = UploadFileForm()
        return render(request, "import_export.html", {'form' : form})
    # if not GET, then proceed
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        if form.cleaned_data['csv_id']:
            up_file_id = request.FILES['csv_id']
            csv_file_id = StringIO(up_file_id.read().decode('UTF-8'))
            replaceIdentifiants(csv_file_id)

        up_file_nom = request.FILES['csv_nom']
        csv_file_nom = StringIO(up_file_nom.read().decode('UTF-8'))
        replaceNomenclature(csv_file_nom)
    return HttpResponseRedirect(reverse("imp-exp"))

def pdf_view(request):
    try:
        return FileResponse(open('app/test1.pdf', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

