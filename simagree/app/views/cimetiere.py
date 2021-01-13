from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest, light_dbRequest
from .pdfgen import *
from .csvparser import *

########## Cimetière ##########


def cimetiere(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))

  items = Nomenclature.objects.using('cimetiere').filter(codesyno=0).values(
      'genre',
      'espece',
      'autorite',
      'variete',
      'forme',
      'taxon_id',
      'id'
  )
  items_taxons = Nomenclature.objects.using('cimetiere').filter(codesyno=0).values_list(
      'taxon_id'
  )
  taxons = [i[0] for i in items_taxons]

  items_existants = Identifiants.objects.filter(
      taxon__in=taxons).values_list('taxon')

  existants = [i[0] for i in items_existants]

  return render(request, 'cimetiere.html', {
      'shrooms': items,
      'existants': existants
  })


def restoreTaxon(request, tax):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  id = Identifiants.objects.using('cimetiere').get(taxon=tax)
  id_cpy = Identifiants.objects.using('cimetiere').get(taxon=tax)
  noms = Nomenclature.objects.using('cimetiere').filter(taxon=tax)
  id_cpy.id = idMaxId()
  id_cpy.save(using='default')

  id_def = Identifiants.objects.get(taxon=tax)
  for i in noms:
    obj = duplicateNomenc(i)
    obj.id = nomencMaxId()
    obj.taxon = id_def
    obj.save(using='default')

  id.delete()
  return redirect(reverse(cimetiere))


def definitiveDelete(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  if request.method == "POST":
    item = Identifiants.objects.using(
        'cimetiere').get(taxon=request.POST.get('taxon'))
    item.delete()
  return redirect(reverse(cimetiere))