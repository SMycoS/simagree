from django.shortcuts import render

# Create your views here.

from .liste import MyList
from .models import Identifiants, Noms

def accueil(req):
    return render(req, 'home.html')

def search(req):
    items = Noms.objects.select_related('taxon').order_by('taxon').values('taxon','nom','taxon__comestible','taxon__sms')
    return render(req, 'search.html',{'shrooms' : items} )