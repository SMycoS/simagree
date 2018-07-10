from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


# Create your views here.

from .liste import MyList
from .models import Identifiants, NotesEco, Themes, Nomenclature
from .forms import SearchForm, AddFormNom, AddFormId, AddFormPartial, ConnexionForm
from .searchparser import dbRequest

def accueil(req):
    return render(req, 'home.html')

def search(req):
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
            return render(req, 'search.html', {'form' : form, 'shrooms' : items})
    else:
        form = SearchForm(auto_id=True)

    return render(req, 'search.html',{'form' : form} )


def add(req):
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
            values.save(using='simagree')

    return render(req, 'add.html', {'formset' : id_form, 'form2' : nom_form})

def addPartial(req):
    if req.method == 'GET':
        nom_form = AddFormPartial(req.GET or None)
    elif req.method == 'POST':
        nom_form = AddFormPartial(req.POST)
        if nom_form.is_valid():
            id = nom_form.cleaned_data['tax']
            print(id, type(id))
            inst = Identifiants.objects.using('simagree').get(taxon = id)
            values = nom_form.save(commit = False)
            values.taxon = inst
            values.save(using='simagree')
    return render(req, 'add_partial.html', {'form' : nom_form})

def details(req, tax):
    item = Identifiants.objects.using('simagree').get(taxon = tax)
    return render(req, 'details.html', {'shroom' : item})

def deleteConfirm(req):
    if req.method == 'POST':
        item = Nomenclature.objects.using('simagree').get(id = req.POST.get('ident'))
        item.delete()
        return HttpResponseRedirect(req.POST.get('next'))

def modify(req, id):
    inst_nom = Nomenclature.objects.using('simagree').get(id = id)
    inst_id = Identifiants.objects.using('simagree').get(taxon=inst_nom.taxon_id)
    # première requête
    if req.method == 'GET':
        id_form = AddFormId(req.GET or None, instance=inst_id)
        nom_form = AddFormNom(req.GET or None, instance=inst_nom)
    # après envoi du formulaire
    elif req.method == 'POST':
        if int(req.POST.get('taxon')) != inst_id.taxon:
            id_form = AddFormId(req.POST)
        else:
            id_form = AddFormId(req.POST, instance=inst_id)
            print('CAS 2')
        nom_form = AddFormNom(req.POST, instance=inst_nom)
        if id_form.is_valid() and nom_form.is_valid():
            if id_form.cleaned_data['taxon'] != inst_id.taxon:
                new_inst = id_form.save(commit = False)
                new_inst.save(using='simagree')
                # sauvegarde dans la table Nomenclature
                Nomenclature.objects.using('simagree').filter(taxon=inst_id.taxon).update(taxon=new_inst)
                inst_id.delete()
                values = nom_form.save(commit = False)
                values.taxon = new_inst
                values.save(using='simagree')
            else:
                # sauvegarde dans la table Identifiants
                inst_id = id_form.save(commit = False)
                inst_id.save(using='simagree')

                # sauvegarde dans la table Nomenclature
                values = nom_form.save(commit = False)
                values.taxon = inst_id
                values.save(using='simagree')

    return render(req, 'modify.html', {'formset' : id_form, 'form2' : nom_form})

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