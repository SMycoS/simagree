from django.shortcuts import render
from django.http import HttpResponseRedirect


# Create your views here.

from .liste import MyList
from .models import Identifiants, NotesEco, Themes, Nomenclature
from .forms import SearchForm, AddFormNom, AddFormId, AddFormPartial
from .searchparser import dbRequest

def accueil(req):
    return render(req, 'home.html')

def search(req):
    # if this is a POST request we need to process the form data
    if req.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(req.POST, auto_id=True)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            items = dbRequest(form.cleaned_data)
            return render(req, 'search.html', {'form' : form, 'shrooms' : items})

    # if a GET (or any other method) we'll create a blank form
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
