from django.shortcuts import render
from django.http import HttpResponseRedirect


# Create your views here.

from .liste import MyList
from .models import Identifiants, NotesEco, Themes, Nomenclature
from .forms import SearchForm, MyModelForm, MyMod
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
    if req.method == 'GET':
        #form = AddForm(req.GET or None)
        formset = MyMod(req.GET or None)
        f2 = MyModelForm(req.GET or None)
    elif req.method == 'POST':
        #form = AddForm(req.POST)
        formset = MyMod(req.POST)
        f2 = MyModelForm(req.POST)
        if formset.is_valid():
            inst = formset.save(commit = False)
            inst.save(using='simagree')
            values = f2.save(commit = False)
            print(req)
            values.taxon = inst
            values.save(using='simagree')
    return render(req, 'add.html', {'formset' : formset, 'form2' : f2})
