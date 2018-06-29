from django.shortcuts import render

# Create your views here.

from .liste import MyList
from .models import Identifiants, NotesEco, Themes, Nomenclature

def accueil(req):
    return render(req, 'home.html')

def search(req):
    #requete sur la base simagree
    #il faut specifier les valeurs a afficher car par defaut seules les valeurs de la table principale sont renvoyees
    items = Nomenclature.objects.using('simagree').select_related('taxon').values(
        'taxon_id',
        'genre',
        'espece',
        'taxon__sms',
        'taxon__comestible',
        'taxon__noms'
        )
    return render(req, 'search.html',{'shrooms' : items} )