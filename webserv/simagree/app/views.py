from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.db.models import Q, Max
from django.core import serializers
from wsgiref.util import FileWrapper
from django.template import Context, loader
from django.contrib import messages
from django.conf import settings

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

def nb_pages(total, per_page):
    res = total // per_page
    if total - (res * per_page) > 0:
        return res + 1
    else:
        return res
        
def genSyno(instance, valide = None):
    taxon = instance.taxon
    if valide is None:
        valide = Nomenclature.objects.filter(Q(taxon = taxon) & Q(codesyno = 0)).values('genre')[0]['genre']
    else:
        valide = valide.genre
    if (valide == instance.genre) and (instance.codesyno != 1):
        Nomenclature.objects.filter(id = instance.id).update(codesyno = 1)
    elif (instance.codesyno != 2):
        Nomenclature.objects.filter(id = instance.id).update(codesyno = 2)

########## Vues pour la connexion ##########

def accueil(request):
    return render(request, 'home.html')

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
                messages.success(request, 'Vous êtes à présent authentifié !')
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


def search(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    # if this is a POST request we need to process the form data
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET or None, auto_id=True)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            items = dbRequest(form.cleaned_data, (req_size, int(request.GET['page'])))
            return render(request, 'search.html', {
                'form' : form,
                'shrooms' : items[1],
                'total' : items[0],
                'pages' : range(1, nb_pages(items[0], req_size) + 1),
                'pages_int' : nb_pages(items[0], req_size)
                })
    else:
        form = SearchForm(auto_id=True)

    return render(request, 'search.html',{'form' : form})


########## Vues pour la gestion des champignons ##########

def add(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    # récupération de l'ensemble des taxons
    # première requête
    if request.method == 'GET':
        id_form = AddFormId(request.GET or None)
        nom_form = AddFormNom(request.GET or None)
        search_form = LightSearchForm()
    # après envoi du formulaire
    elif request.method == 'POST' and request.POST['action'] == "add":
        id_form = AddFormId(request.POST)
        nom_form = AddFormNom(request.POST)
        search_form = LightSearchForm(request.POST)
        if id_form.is_valid() and nom_form.is_valid():
            # sauvegarde dans la table Identifiants
            inst = id_form.save(commit = False)
            # génération automatique du numéro de fiche (max + 1)
            num_fiche = Identifiants.objects.all().aggregate(Max('fiche'))['fiche__max']
            num_fiche += 1
            inst.fiche = num_fiche
            inst.save()
            # sauvegarde dans la table Nomenclature
            values = nom_form.save(commit = False)
            values.taxon = inst
            values.codesyno = 0
            values.save()
            return redirect(reverse(details, kwargs = {'id_item' : values.id}))
    # Recherche
    else:
        id_form = AddFormId()
        nom_form = AddFormNom()
        search_form = LightSearchForm(request.POST)
        if search_form.is_valid():
            items = light_dbRequest(search_form.cleaned_data)
            return render(request, 'add.html', {
                'form' : id_form, 
                'form2' : nom_form,
                'searchform' : search_form, 
                'results':items
                })
    return render(request, 'add.html', {'form' : id_form, 'form2' : nom_form,'searchform' : search_form})


def addPartial(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    if request.method == 'GET':
        nom_form = AddFormPartial(request.GET or None)
        search_form = LightSearchForm()
    elif request.method == 'POST' and request.POST['action'] == "add":
        nom_form = AddFormPartial(request.POST)
        search_form = LightSearchForm(request.POST)
        if nom_form.is_valid():
            id = nom_form.cleaned_data['tax']
            inst = Identifiants.objects.get(taxon = id)
            values = nom_form.save(commit = False)
            values.taxon = inst
            # vérification du code synonyme
            if values.codesyno == 0:
                old_valide = Nomenclature.objects.filter(Q(taxon=inst.taxon) & Q(codesyno=0))[0]
                genSyno(old_valide, valide = values)
            elif values.codesyno == 3:
                if (Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3)).count()) > 0:
                    old_usuel = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3))[0]
                    genSyno(old_usuel)
            values.save()
            return redirect(reverse(details, kwargs = {'id_item' : values.id}))
    else:
        nom_form = AddFormPartial()
        search_form = LightSearchForm(request.POST)
        if search_form.is_valid():
            items = light_dbRequest(search_form.cleaned_data)
            return render(request, 'add_partial.html', {
                'form' : nom_form,
                'searchform' : search_form, 
                'results':items
                })
    
    return render(request, 'add_partial.html', {'form' : nom_form, 'searchform' : search_form})

def details(request, id_item):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    # Récupération de l'objet et de tous ses attributs nécessaires
    item = Nomenclature.objects.select_related('taxon').filter(id = id_item).values(
        'taxon_id',
        'taxon__fiche',
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
        'date'
        )[0]
    
    # Récupération de la classification correspondante au nom valide
    if item['codesyno'] != 0:
        genre_cla = Nomenclature.objects.filter(Q(taxon_id = item['taxon_id']) & Q(codesyno = 0)).values('genre')[0]['genre']
    else:
        genre_cla = item['genre']
    cla = Classification.objects.filter(genre__iexact = genre_cla).all()

    try:    
        item['taxon__noms'] = item['taxon__noms'].splitlines()
    except:
        pass
    try:
        others = Nomenclature.objects.filter(Q(taxon = item['taxon_id']) & ~Q(id = id_item)).values('genre', 'espece', 'id', 'codesyno', 'variete', 'autorite', 'forme')
        return render(request, 'details.html', {'shroom' : item, 'classification' : cla, 'others' : others})
    except:
        return render(request, 'details.html', {'shroom' : item, 'classification' : cla})

def deleteConfirm(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    if request.method == 'POST':
        item = Nomenclature.objects.get(id = request.POST.get('ident'))
        item.delete()
        return HttpResponseRedirect(request.POST.get('next'))

def deleteTaxon(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    if request.method == 'POST':
        item = Identifiants.objects.get(taxon = request.POST.get('taxon'))
    
        # Copie dans la db cimetiere de l'ID
        item_cpy = Identifiants.objects.get(taxon = request.POST.get('taxon'))
        item_cpy.pk = None
        item_cpy.save(using='cimetiere')

        # Copie dans la db cimetiere des noms
        nom = Nomenclature.objects.filter(taxon = request.POST.get('taxon'))
        # Recharge de l'objet dans la db cimetiere
        inst_id = Identifiants.objects.using('cimetiere').get(taxon = request.POST.get('taxon'))
        for i in nom:
            i.pk = None
            i.taxon = inst_id
            i.save(using='cimetiere')

        # Supression de la db principale
        item.delete()
        return HttpResponseRedirect(request.POST.get('next'))

def modify(request, id):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    inst_nom = Nomenclature.objects.get(id = id)
    old_code = inst_nom.codesyno
    others = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon)).order_by('codesyno').values(
        'genre',
        'espece',
        'variete',
        'forme',
        'codesyno',
        'autorite',
        'id'
    )
    others_json = serializers.serialize("json", Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & ~Q(codesyno = 0)))
    # première requête
    if request.method == 'GET':
        nom_form = ModForm(request.GET or None, instance=inst_nom)
    # après envoi du formulaire
    elif request.method == 'POST':
        nom_form = ModForm(request.POST, instance = inst_nom)
        if nom_form.is_valid():
            # sauvegarde dans la table Nomenclature
            
            values = nom_form.save(commit = False)
            values.codesyno = int(values.codesyno)
            # vérification du code synonyme (si il y a eu changement)
            if (values.codesyno != old_code):
                # Cas : anciennement valide (passage VALIDE -> SYN)
                if old_code == 0:
                    # On récupère l'id du nouveau valide
                    new_valide = int(request.POST['changeCode'])
                    # Mise à jour dans la BDD
                    valide = Nomenclature.objects.filter(id = new_valide)
                    valide.update(codesyno = 0)
                    # si un synonyme était déjà SYN USUEL, on le change en SYN
                    if values.codesyno == 3:
                        if (Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3)).count()) > 0:
                            old_usuel = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3))[0]
                            genSyno(old_usuel)
                    synonymes = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno__in = [1,2]))
                    for s in synonymes:
                        gensyno(s, valide = valide[0])
                # Cas : synonyme
                else:
                    # passage SYN -> VALIDE
                    if values.codesyno == 0:
                        old_valide = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 0))
                        # Etat dans lequel mettre l'ancien VALIDE
                        old_state = int(request.POST['changeCode'])
                        # SYN (classique)
                        if old_state == 1:
                            genSyno(old_valide[0], valide = values) # mise à jour automatique avec le code 1 ou 2
                        # SYN USUEL
                        else:
                            # si un synonyme était déjà SYN USUEL, on le change en SYN
                            if (Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3)).count()) > 0:
                                old_usuel = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3))[0]
                                genSyno(old_usuel, valide = values)

                            # changement de l'ancien VALIDE en SYN USUEL
                            old_valide.update(codesyno = 3)
                        # On met à jour de la des synonymes
                        synonymes = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno__in = [1,2]))
                        for s in synonymes:
                            genSyno(s, valide = values)
                    # passage SYN -> SYN USUEL
                    else:
                        # si un synonyme était déjà SYN USUEL, on le change en SYN
                        if (Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3)).count()) > 0:
                            old_usuel = Nomenclature.objects.filter(Q(taxon = inst_nom.taxon) & Q(codesyno = 3))[0]
                            genSyno(old_usuel)


            values.save()
            return redirect(reverse(details, kwargs = {'id_item' : values.id}))

    return render(request, 'modify.html', {
        'form' : nom_form,
        'others' : others,
        'data' : others_json,
        'state' : inst_nom.codesyno
        })


def modifyTaxon(request, tax):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    inst = Identifiants.objects.get(taxon = tax)
    shrooms = Nomenclature.objects.filter(taxon = tax).order_by('codesyno').values(
        'genre',
        'espece',
        'variete',
        'forme',
        'autorite',
        'codesyno',
        'taxon'
    )
    if request.method == 'GET':
        form = ModFormTax(request.GET or None, instance = inst)
    elif request.method == 'POST':
        form = ModFormTax(request.POST, instance = inst)
        if form.is_valid():
            values = form.save(commit = False)
            print(values)
            values.save()
            valide = Nomenclature.objects.filter(Q(taxon = values.taxon) & Q(codesyno = 0))[0]
            return redirect(reverse(details, kwargs = {'id_item' : valide.id}))
    return render(request, 'modify_tax.html', {'form' : form, 'shrooms' : shrooms})




########## Vues pour la gestion des thèmes ##########

def themes(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    themes_list = Themes.objects.order_by('theme').all()
    if request.method == 'GET':
        form = AddThemeForm(request.GET or None)
    elif request.method == 'POST' and request.POST["action"] == "add":
        form = AddThemeForm(request.POST)
        if form.is_valid():
            inst = form.save(commit = False)
            inst.save()
    elif request.method == 'POST' and request.POST["action"] == "edit":
        form = AddThemeForm()
        Themes.objects.filter(id = request.POST.get('ident')).update(titre = request.POST.get('titre'))
        
    return render(request, 'add_theme.html', {'form' : form, 'themes_list' : themes_list})

def deleteTheme(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    if request.method == 'POST':
        item = Themes.objects.get(id = request.POST.get('ident'))
        item.delete()
        return redirect(reverse(themes))


########## Vues pour la gestion des pdf ##########

def send_file(request, tax, type_fiche):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    #Suppression des fiches si trop nombreuses dans le dossier
    dir_fiches = settings.BASE_DIR +  '/app/pdf_assets/fiches/'
    try:
        files = next(os.walk(dir_fiches))[2]
    except:
        raise Http404()
    if len(files) > 20:
        for i in files:
            os.remove(dir_fiches + i)

    # Generation du pdf
    # Objet
    item = Nomenclature.objects.select_related('taxon').filter(Q(taxon = tax) & Q(codesyno = 0)).values(
        'taxon__fiche',
        'genre',
        'espece',
        'variete',
        'taxon__noms',
        'forme' ,
        'taxon__comestible',
        'taxon__notes',
        'taxon__ecologie',
        'taxon__theme1',
        'taxon__theme2',
        'taxon__theme3',
        'taxon__theme4',
        'taxon_id'
    )[0]


    vars = {}

    usuel = Nomenclature.objects.filter(Q(taxon = tax) & Q(codesyno = 3)).values('genre', 'espece', 'variete', 'forme')

    if len(usuel) > 0:
        try:
            vars['usuel_genre'] = usuel[0]['genre']
            vars['usuel_espece'] = usuel[0]['espece']
            vars['usuel_variete'] = none2string(usuel[0]['variete'])
            vars['usuel_forme'] = none2string(usuel[0]['forme'])
        except:
            raise Http404()
    
    try:
        vars['taxon'] = str(item['taxon_id'])
        vars['fiche'] = none2string(item['taxon__fiche'])
        vars['genre'] = item['genre']
        vars['espece'] = item['espece']
        vars['variete'] = none2string(item['variete'])
        vars['forme'] = none2string(item['forme'])
        vars['noms'] = none2string(item['taxon__noms'])
        vars['comestibilite'] = none2string(item['taxon__comestible'])
        vars['obs'] = [none2string(item['taxon__notes']), none2string(item['taxon__ecologie'])]
        fullpath = dir_fiches + none2string(item['taxon__fiche']) + '.pdf'
    except Exception as e:
        raise Http404()
    try:
        if type_fiche == "classique":
            # Présence d'un thème ?
            has_theme = [item['taxon__theme1'], item['taxon__theme2'], item['taxon__theme3'], item['taxon__theme4']]
            has_theme = not (has_theme.count(None) == len(has_theme))
            if has_theme:
                vars['theme'] = 'Th'
            generateFiche(fullpath, vars)
        else:
            vars['theme_code'] = type_fiche
            titre = Themes.objects.get(theme = type_fiche).titre
            vars['theme_titre'] = none2string(titre)
            generateFicheTheme(fullpath, vars)
        return FileResponse(open(fullpath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

########## Vues pour la gestion des fiches récolte (EBAUCHE) ##########
"""
def editList(request, id_liste):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    liste_instance = ListeRecolte.objects.get(id = id_liste)
    taxons = liste_instance.taxons.all()
    liste_taxons = [i.taxon for i in taxons]
    # calcul du total de pages
    total = Nomenclature.objects.all().filter(~Q(taxon__in = liste_taxons)).count()
    pages = nb_pages(total, 1000)
    if request.method == "POST" and request.POST['action'] == "edit":
        listeform = EditListTaxonsForm(
            request.POST, 
            instance=liste_instance,
            taxons=liste_taxons, 
            page=int(request.GET['page'])
        )
        if listeform.is_valid():
            liste_taxons = [int(i) for i in listeform.cleaned_data['selectf']]
            # suppression de toutes les relations existantes
            liste_instance.taxons.clear()
            # ajout des relations
            # add() prend un nombre variable d'arguments
            # donc on "éclate" le QuerySet
            liste_instance.taxons.add(*(Identifiants.objects.all().filter(
                Q(taxon__in = liste_taxons))))
            listeform = EditListTaxonsForm(
                instance = liste_instance,
                taxons=liste_taxons,
                page=int(request.GET['page'])
            )
            
    else:
        listeform = EditListTaxonsForm(
            instance = liste_instance,
            taxons=liste_taxons,
            page=int(request.GET['page'])
        )
    return render(request, 'listes_create.html', {
        'listeform' : listeform,
        'pages_int' : pages,
        'pages' : range(1, pages + 1),
        'liste' : id_liste
        })

def showLists(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    listes = ListeRecolte.objects.all().only('lieu', 'date', 'id')
    lieux = LieuRecolte.objects.all()
    modal_display = ''
    if request.method == "POST" and request.POST['action'] == "lieu":
        liste_form = AddListForm()
        lieu_form = AddLieuForm(request.POST)
        modal_display = "lieu"
        if lieu_form.is_valid():
            lieu_form.save()
    elif request.method == "POST" and request.POST['action'] == "liste":
        liste_form = AddListForm(request.POST)
        lieu_form = AddLieuForm()
        modal_display = "liste"
        if liste_form.is_valid():
            liste_form.save()
    elif request.method == "POST" and request.POST['action'] == "deleteLieu":
        liste_form = AddListForm()
        lieu_form = AddLieuForm()
        lieu = LieuRecolte.objects.get(id = request.POST['ident'])
        lieu.delete()
    else:
        liste_form = AddListForm()
        lieu_form = AddLieuForm()

    return render(request, 'listes.html', {
        'listes' : listes,
        'lieux' : lieux,
        'listeform' : liste_form,
        'lieuform' : lieu_form,
        'modal_display' : modal_display
        })

def detailsList(request, id_liste):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    liste = ListeRecolte.objects.get(id = id_liste)
    taxons = []
    for i in liste.taxons.all():
        if (int(i.taxon) not in taxons):
            taxons.append(int(i.taxon))
    items = Nomenclature.objects.select_related('taxon').filter(Q(taxon__in = taxons) & Q(codesyno = 0)).values('genre', 'espece')
    return render(request, 'listes.html', {'liste' : liste, 'items' : items})

def modList(request, id_liste):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    liste = ListeRecolte.objects.get(id = id_liste)
    all_taxons = Nomenclature.objects.select_related('taxon').only('taxon_id', 'genre', 'espece')
    if request.method == "POST":
        form = AddListForm(request.POST, instance = liste)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = AddListForm(instance = liste)

"""
########## Vues pour l'import / export de la base en csv ##########

def csvIdent(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
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
        'data' : Identifiants.objects.all()
    }
    response.write(template.render(c))
    return response

def csvNomenc(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
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
        'data' : Nomenclature.objects.all().order_by('taxon_id', 'codesyno')
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
            if replaceIdentifiants(csv_file_id):
                messages.success(request, 'La base Identifiants a bien été mise à jour.')
            else:
                messages.error(request, "Une erreur est survenue lors de l'import de la base Identifiants.")
                return HttpResponseRedirect(reverse("imp-exp"))
        if form.cleaned_data['csv_classification']:
            up_file_cla = request.FILES['csv_classification']
            csv_file_cla = StringIO(up_file_cla.read().decode('UTF-8'))
            if replaceClassification(csv_file_cla):
                messages.success(request, 'La base Classification a bien été mise à jour.')
            else:
                messages.error(request, "Une erreur est survenue lors de l'import de la base Classification.")
                return HttpResponseRedirect(reverse("imp-exp"))
        if form.cleaned_data['csv_nom']:
            up_file_nom = request.FILES['csv_nom']
            csv_file_nom = StringIO(up_file_nom.read().decode('UTF-8'))
            if replaceNomenclature(csv_file_nom):
                messages.success(request, 'La base Nomenclature a bien été mise à jour.')
            else:
                messages.error(request, "Une erreur est survenue lors de l'import de la base Nomenclature.")
                return HttpResponseRedirect(reverse("imp-exp"))
    return HttpResponseRedirect(reverse("imp-exp"))

########## Cimetière ##########

def cimetiere(request):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))

    items = Nomenclature.objects.using('cimetiere').filter(codesyno = 0).values(
        'genre',
        'espece',
        'autorite',
        'variete',
        'forme',
        'taxon_id'
    )
    items_taxons = Nomenclature.objects.using('cimetiere').filter(codesyno = 0).values_list(
        'taxon_id'
    )
    taxons = [i[0] for i in items_taxons]

    items_existants = Identifiants.objects.filter(taxon__in = taxons).values_list('taxon')
    
    existants = [i[0] for i in items_existants]

    return render(request, 'cimetiere.html', {
        'shrooms' : items,
        'existants' : existants
    })

def restoreTaxon(request, tax):
    if not request.user.is_authenticated:
        return redirect(reverse(connexion))
    if not (request.user.groups.filter(name='Administrateurs').exists()):
        return redirect(reverse(accueil))
    id = Identifiants.objects.using('cimetiere').get(taxon = tax)
    id_cpy = Identifiants.objects.using('cimetiere').get(taxon = tax)
    noms = Nomenclature.objects.using('cimetiere').filter(taxon = tax)
    id_cpy.pk = None
    id_cpy.save(using='default')

    id_def = Identifiants.objects.get(taxon = tax)
    for i in noms:
        i.pk = None
        i.taxon = id_def
        i.save(using='default')

    id.delete()
    return redirect(reverse(cimetiere))

    
    
