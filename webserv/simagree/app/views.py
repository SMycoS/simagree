from django.shortcuts import render

# Create your views here.

from .liste import MyList

def accueil(req):
    return render(req, 'home.html')

def search(req):
    items = MyList.getShrooms
    return render(req, 'search.html',{'shrooms' : items} )