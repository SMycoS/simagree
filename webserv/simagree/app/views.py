from django.shortcuts import render
from django.http import HttpResponseRedirect


# Create your views here.

from .liste import MyList
from .models import Identifiants, NotesEco, Themes, Nomenclature
from .forms import SearchForm
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
            print(items)
            return render(req, 'form.html', {'form' : form, 'shrooms' : items})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm(auto_id=True)

    return render(req, 'search.html',{'form' : form} )

def searchForm(req):
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
            print(items)
            return render(req, 'form.html', {'form' : form, 'shrooms' : items})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm(auto_id=True)
    
    return render(req, 'form.html', {'form' : form})