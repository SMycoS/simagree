from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db.models import Q
from django.core import serializers
from wsgiref.util import FileWrapper
import os




# Create your views here.

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest
from .pdfgen import generateFiche

def accueil(req):
    return render(req, 'home.html')

def search(req):
    if req.user.is_authenticated:
        # if this is a POST request we need to process the form data
        if req.method == 'GET':
            # create a form instance and populate it with data from the request:
            form = SearchForm(req.GET or None, auto_id=True)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                items = dbRequest(form.cleaned_data)
                print(items)
                return render(req, 'search.html', {'form' : form, 'shrooms' : items})
        else:
            form = SearchForm(auto_id=True)

        return render(req, 'search.html',{'form' : form} )
    else:
        return redirect(reverse(connexion))


########## Vues pour la gestion des champignons ##########

def add(req):
    if req.user.is_authenticated:
        # récupération de l'ensemble des taxons
        all_taxons = Nomenclature.objects.using('simagree').select_related('taxon').only('taxon_id', 'genre', 'espece')
        data = serializers.serialize("json", all_taxons)
        # première requête
        if req.method == 'GET':
            id_form = AddFormId(req.GET or None)
            nom_form = AddFormNom(req.GET or None)
        # après envoi du formulaire
        elif req.method == 'POST':
            id_form = AddFormId(req.POST)
            nom_form = AddFormNom(req.POST)
            if id_form.is_valid() and nom_form.is_valid():
                # sauvegarde dans la table Identifiants
                inst = id_form.save(commit = False)
                inst.save(using='simagree')

                # sauvegarde dans la table Nomenclature
                values = nom_form.save(commit = False)
                values.taxon = inst
                # vérification du code synonyme
                if values.codesyno == 0:
                    Nomenclature.objects.using('simagree').filter(Q(taxon=new_inst.taxon) & Q(codesyno=0)).update(codesyno=1)
                values.save(using='simagree')

        return render(req, 'add.html', {'form' : id_form, 'form2' : nom_form,'all_tax' : data})
    else:
        return redirect(reverse(connexion))


def addPartial(req):
    if req.user.is_authenticated:
        all_taxons = Nomenclature.objects.using('simagree').select_related('taxon').only('taxon_id', 'genre', 'espece')
        data = serializers.serialize("json", all_taxons)
        if req.method == 'GET':
            nom_form = AddFormPartial(req.GET or None)
        elif req.method == 'POST':
            nom_form = AddFormPartial(req.POST)
            if nom_form.is_valid():
                id = nom_form.cleaned_data['tax']
                inst = Identifiants.objects.using('simagree').get(taxon = id)
                values = nom_form.save(commit = False)
                values.taxon = inst
                # vérification du code synonyme
                if values.codesyno == 0:
                    Nomenclature.objects.using('simagree').filter(Q(taxon=inst.taxon) & Q(codesyno=0)).update(codesyno=1)
                values.save(using='simagree')
        return render(req, 'add_partial.html', {'form' : nom_form, 'all_tax' : data})
    else:
        return redirect(reverse(connexion))

def details(req, id_item):
    if req.user.is_authenticated:
        item = Nomenclature.objects.using('simagree').select_related('taxon').filter(id = id_item).values('taxon_id', 'taxon__noms', 'taxon__comestible', 'taxon__sms', 'codesyno', 'genre', 'espece', 'variete', 'forme')
        try:
            others = Nomenclature.objects.using('simagree').filter(Q(taxon = item[0]['taxon_id']) & ~Q(id = id_item)).values('genre', 'espece', 'id', 'codesyno')
            return render(req, 'details.html', {'shroom' : item[0], 'others' : others})
        except:
            return render(req, 'details.html', {'shroom' : item[0]})
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

########## Vues pour la connexion ##########

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
    else:
        form = ConnexionForm()

    return render(request, 'login.html', locals())

def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))



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

def send_file(request, tax):
    
    # Generation du pdf
    item = Nomenclature.object.using('simagree').select_related('taxon').filter(id = rax).values(
        'theme',
        'taxon__fiche',
        'genre',
        'espece',
        'variete',
        'taxon__noms',
        'forme' ,
        'taxon__comestible',
    )
    vars = {
        'theme' : item['theme'],
        'fiche' : item['taxon__fiche'],
        'genre' : item['genre'],
        'espece' : item['espece'],
        'variete' : item['variete'],
        'noms' : item['taxon__noms'],
        'forme' : item['forme'],
        'comestibilite' : item['taxon__comestible'],
        'obs' : "C'est joli",
        }
    # save_name = '/static/fiches/' + id_item + '.pdf'
    generateFiche(item['taxon_fiche'] + '.pdf', vars)

    # Envoi de fichier

    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    filename = item['taxon__fiche'] + '.pdf'                               
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

########## Vues pour la gestion des fiches récolte ##########

def addList(req):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    all_taxons = Nomenclature.objects.using('simagree').select_related('taxon').only('taxon_id', 'genre', 'espece')
    if req.method == "POST":
        form = AddListForm(req.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = AddListForm()

    return render(req, 'listes_create.html', {'form' : form, 'all_tax' : all_taxons})

def showLists(req):
    if not req.user.is_authenticated:
        return redirect(reverse(connexion))
    #listes = ListeRecolte.objects.using('simagree').all().values('date', 'lieu', 'id')
    listes = []
    return render(req, 'listes.html', {'listes' : listes})

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