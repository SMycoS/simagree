from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404, HttpResponseServerError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.db.models import Q, Max, F
from django.core import serializers
from wsgiref.util import FileWrapper
from django.template import Context, loader
from django.contrib import messages
from django.conf import settings
from copy import deepcopy

import os
import datetime
import csv
import traceback
import codecs
from io import StringIO


# Create your views here.

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest, light_dbRequest
from .pdfgen import *
from .csvparser import *

### Divers ###

req_size = 500  # nombre d'objets par requête de recherche


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


def genSyno(instance, valide=None):
  taxon = instance.taxon
  if valide is None:
    valide = Nomenclature.objects.filter(
        Q(taxon=taxon) & Q(codesyno=0)).values('genre')[0]['genre']
  else:
    valide = valide.genre
  if (valide == instance.genre) and (instance.codesyno != 1):
    Nomenclature.objects.filter(id=instance.id).update(
        codesyno=1, date=datetime.date.today())
  elif (instance.codesyno != 2):
    Nomenclature.objects.filter(id=instance.id).update(
        codesyno=2, date=datetime.date.today())


def duplicateNomenc(instance):
  obj = Nomenclature(
      codesyno=instance.codesyno,
      genre=instance.genre,
      espece=instance.espece,
      variete=instance.variete,
      forme=instance.forme,
      autorite=instance.autorite,
      biblio1=instance.biblio1,
      biblio2=instance.biblio2,
      biblio3=instance.biblio3,
      moser=instance.moser,
      date=instance.date
  )
  return obj


def idMaxId():
  return Identifiants.objects.all().aggregate(Max('id'))['id__max'] + 1


def nomencMaxId():
  return Nomenclature.objects.all().aggregate(Max('id'))['id__max'] + 1

########## Vues pour la connexion ##########


def accueil(request):
  return render(request, 'home.html')


def about(request):
  return render(request, 'about.html')


def connexion(request):
  error = False
  if request.method == "POST":
    form = ConnexionForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data["username"]
      password = form.cleaned_data["password"]
      # Nous vérifions si les données sont correctes
      user = authenticate(username=username, password=password)
      if user:  # Si l'objet renvoyé n'est pas None
        login(request, user)  # nous connectons l'utilisateur
        messages.success(request, 'Vous êtes à présent authentifié !')
      else:  # sinon une erreur sera affichée
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
      items = dbRequest(form.cleaned_data,
                        (req_size, int(request.GET['page'])))
      return render(request, 'search.html', {
          'form': form,
          'shrooms': items[1],
          'total': items[0],
          'pages': range(1, nb_pages(items[0], req_size) + 1),
          'pages_int': nb_pages(items[0], req_size)
      })
  else:
    form = SearchForm(auto_id=True)

  return render(request, 'search.html', {'form': form})


########## Vues pour la gestion des champignons ##########

def add(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  max_tax = Identifiants.objects.all().aggregate(Max('taxon'))['taxon__max']
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
      inst = id_form.save(commit=False)
      # génération automatique du numéro de fiche (max + 1)
      num_fiche = Identifiants.objects.all().aggregate(Max('fiche'))[
          'fiche__max']
      num_fiche += 1
      inst.fiche = num_fiche
      inst.id = idMaxId()
      inst.save()
      # sauvegarde dans la table Nomenclature
      values = nom_form.save(commit=False)
      values.taxon = inst
      values.date = datetime.date.today()
      values.codesyno = 0
      values.id = nomencMaxId()
      values.save()
      return redirect(reverse(details, kwargs={'id_item': values.id}))
  elif request.method == 'POST' and request.POST['action'] == "result":
    id_form = AddFormId()
    nom_form = AddFormNom()
    search_form = LightSearchForm(request.POST)
    if search_form.is_valid():
      items = light_dbRequest(search_form.cleaned_data)
      selected_tax = int(request.POST['prevTax1'])
      # selection +/- 500
      selected_close = Nomenclature.objects.filter(Q(taxon_id__gte=selected_tax - 500) & Q(taxon_id__lte=selected_tax + 500)).values(
          'taxon_id',
          'genre',
          'espece',
          'variete',
          'forme',
      )
      return render(request, 'add.html', {
          'form': id_form,
          'form2': nom_form,
          'searchform': search_form,
          'results': items,
          'results2': selected_close,
          'selected': selected_tax,
          'max_tax': max_tax
      })
  # Recherche
  else:
    id_form = AddFormId()
    nom_form = AddFormNom()
    search_form = LightSearchForm(request.POST)
    if search_form.is_valid():
      items = light_dbRequest(search_form.cleaned_data)
      return render(request, 'add.html', {
          'form': id_form,
          'form2': nom_form,
          'searchform': search_form,
          'results': items,
          'max_tax': max_tax
      })

  return render(request, 'add.html', {'form': id_form, 'form2': nom_form, 'searchform': search_form, 'max_tax': max_tax})


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
      inst = Identifiants.objects.get(taxon=id)
      values = nom_form.save(commit=False)
      values.taxon = inst
      values.id = nomencMaxId()
      values.date = datetime.date.today()
      # vérification du code synonyme
      if values.codesyno == 0:
        old_valide = Nomenclature.objects.filter(
            Q(taxon=inst.taxon) & Q(codesyno=0))[0]
        genSyno(old_valide, valide=values)
      elif values.codesyno == 3:
        if (Nomenclature.objects.filter(Q(taxon=inst_nom.taxon) & Q(codesyno=3)).count()) > 0:
          old_usuel = Nomenclature.objects.filter(
              Q(taxon=inst_nom.taxon) & Q(codesyno=3))[0]
          genSyno(old_usuel)
      values.save()
      return redirect(reverse(details, kwargs={'id_item': values.id}))
  else:
    nom_form = AddFormPartial()
    search_form = LightSearchForm(request.POST)
    if search_form.is_valid():
      items = light_dbRequest(search_form.cleaned_data)
      return render(request, 'add_partial.html', {
          'form': nom_form,
          'searchform': search_form,
          'results': items
      })

  return render(request, 'add_partial.html', {'form': nom_form, 'searchform': search_form})


def details(request, id_item):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  # Récupération de l'objet et de tous ses attributs nécessaires
  item = Nomenclature.objects.select_related('taxon').filter(id=id_item).values(
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
    genre_cla = Nomenclature.objects.filter(
        Q(taxon_id=item['taxon_id']) & Q(codesyno=0)).values('genre')[0]['genre']
  else:
    genre_cla = item['genre']
  cla = Classification.objects.filter(genre__iexact=genre_cla).all()

  try:
    item['taxon__noms'] = item['taxon__noms'].splitlines()
  except:
    pass
  try:
    others = Nomenclature.objects.filter(Q(taxon=item['taxon_id']) & ~Q(id=id_item)).values(
        'genre', 'espece', 'id', 'codesyno', 'variete', 'autorite', 'forme')
    return render(request, 'details.html', {'shroom': item, 'classification': cla, 'others': others})
  except:
    return render(request, 'details.html', {'shroom': item, 'classification': cla})


def deleteConfirm(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  if request.method == 'POST':
    item = Nomenclature.objects.get(id=request.POST.get('ident'))
    item.delete()
    return HttpResponseRedirect(request.POST.get('next'))


def deleteTaxon(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  if request.method == 'POST':
    item = Identifiants.objects.get(taxon=request.POST.get('taxon'))

    # Copie dans la db cimetiere de l'ID
    item_cpy = Identifiants.objects.get(taxon=request.POST.get('taxon'))
    item_cpy.id = None
    item_cpy.save(using='cimetiere')

    # Copie dans la db cimetiere des noms
    nom = Nomenclature.objects.filter(taxon=request.POST.get('taxon'))
    # Recharge de l'objet dans la db cimetiere
    inst_id = Identifiants.objects.using(
        'cimetiere').get(taxon=request.POST.get('taxon'))
    for i in nom:
      obj = duplicateNomenc(i)
      obj.id = None
      obj.taxon = inst_id
      obj.save(using='cimetiere')

    # Supression de la db principale
    item.delete()
    return HttpResponseRedirect(request.POST.get('next'))


def modify(request, id):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  inst_nom = Nomenclature.objects.get(id=id)
  old_code = inst_nom.codesyno
  others = Nomenclature.objects.filter(Q(taxon=inst_nom.taxon)).order_by('codesyno').values(
      'genre',
      'espece',
      'variete',
      'forme',
      'codesyno',
      'autorite',
      'id'
  )
  others_json = serializers.serialize(
      "json", Nomenclature.objects.filter(Q(taxon=inst_nom.taxon) & ~Q(codesyno=0)))
  # première requête
  if request.method == 'GET':
    nom_form = ModForm(request.GET or None, instance=inst_nom)
  # après envoi du formulaire
  elif request.method == 'POST':
    nom_form = ModForm(request.POST, instance=inst_nom)
    if nom_form.is_valid():
      # sauvegarde dans la table Nomenclature

      values = nom_form.save(commit=False)
      values.codesyno = int(values.codesyno)
      # vérification du code synonyme (si il y a eu changement)
      if (values.codesyno != old_code):
        # Cas : anciennement valide (passage VALIDE -> SYN)
        if old_code == 0:
          # On récupère l'id du nouveau valide
          new_valide = int(request.POST['changeCode'])
          # Mise à jour dans la BDD
          valide = Nomenclature.objects.filter(id=new_valide)
          try:
            valide.update(codesyno=0, date=datetime.date.today())
          except:
            return HttpResponseServerError()
          else:
            # si un synonyme était déjà SYN USUEL, on le change en SYN
            if values.codesyno == 3:
              if (Nomenclature.objects.filter(Q(taxon=inst_nom.taxon) & Q(codesyno=3)).count()) > 0:
                old_usuel = Nomenclature.objects.filter(
                    Q(taxon=inst_nom.taxon) & Q(codesyno=3))[0]
                genSyno(old_usuel)
            synonymes = Nomenclature.objects.filter(
                Q(taxon=inst_nom.taxon) & Q(codesyno__in=[1, 2]))
            for s in synonymes:
              genSyno(s, valide=valide[0])
        # Cas : synonyme
        else:
          # passage SYN -> VALIDE
          if values.codesyno == 0:
            old_valide = Nomenclature.objects.filter(
                Q(taxon=inst_nom.taxon) & Q(codesyno=0))
            # Etat dans lequel mettre l'ancien VALIDE
            old_state = int(request.POST['changeCode'])
            # SYN (classique)
            if old_state == 1:
              # mise à jour automatique avec le code 1 ou 2
              genSyno(old_valide[0], valide=values)
            # SYN USUEL
            else:
              # si un synonyme était déjà SYN USUEL, on le change en SYN
              if (Nomenclature.objects.filter(Q(taxon=inst_nom.taxon) & Q(codesyno=3)).count()) > 0:
                old_usuel = Nomenclature.objects.filter(
                    Q(taxon=inst_nom.taxon) & Q(codesyno=3))[0]
                genSyno(old_usuel, valide=values)
              # changement de l'ancien VALIDE en SYN USUEL
              old_valide.update(codesyno=3, date=datetime.date.today())
            # On met à jour de la des synonymes
            synonymes = Nomenclature.objects.filter(
                Q(taxon=inst_nom.taxon) & Q(codesyno__in=[1, 2]))
            for s in synonymes:
              genSyno(s, valide=values)
          # passage SYN -> SYN USUEL
          else:
            # si un synonyme était déjà SYN USUEL, on le change en SYN
            if (Nomenclature.objects.filter(Q(taxon=inst_nom.taxon) & Q(codesyno=3)).count()) > 0:
              old_usuel = Nomenclature.objects.filter(
                  Q(taxon=inst_nom.taxon) & Q(codesyno=3))[0]
              genSyno(old_usuel)

      values.date = datetime.date.today()
      values.save()
      return redirect(reverse(details, kwargs={'id_item': values.id}))

  return render(request, 'modify.html', {
      'form': nom_form,
      'others': others,
      'data': others_json,
      'state': inst_nom.codesyno
  })


def modifyTaxon(request, tax):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  inst = Identifiants.objects.get(taxon=tax)
  shrooms = Nomenclature.objects.filter(taxon=tax).order_by('codesyno').values(
      'genre',
      'espece',
      'variete',
      'forme',
      'autorite',
      'codesyno',
      'taxon'
  )
  if request.method == 'GET':
    form = ModFormTax(request.GET or None, instance=inst)
  elif request.method == 'POST':
    form = ModFormTax(request.POST, instance=inst)
    if form.is_valid():
      values = form.save(commit=False)
      values.save()
      valide = Nomenclature.objects.filter(
          Q(taxon=values.taxon) & Q(codesyno=0))[0]
      return redirect(reverse(details, kwargs={'id_item': valide.id}))
  return render(request, 'modify_tax.html', {'form': form, 'shrooms': shrooms})


def modifyNotesEco(request, tax):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Guides').exists()):
    return redirect(reverse(accueil))
  inst = Identifiants.objects.get(taxon=tax)
  shrooms = Nomenclature.objects.filter(taxon=tax).order_by('codesyno').values(
      'genre',
      'espece',
      'variete',
      'forme',
      'autorite',
      'codesyno',
      'taxon'
  )
  if request.method == 'GET':
    form = NotesEcoForm(request.GET or None, instance=inst)
  elif request.method == 'POST':
    form = NotesEcoForm(request.POST, instance=inst)
    if form.is_valid():
      values = form.save(commit=False)
      values.save()
      valide = Nomenclature.objects.filter(
          Q(taxon=values.taxon) & Q(codesyno=0))[0]
      return redirect(reverse(details, kwargs={'id_item': valide.id}))
  return render(request, 'modify_noteseco.html', {'form': form, 'shrooms': shrooms})

########## Vues pour la gestion des thèmes ##########


def themes(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Guides').exists()):
    return redirect(reverse(accueil))
  themes_list = Themes.objects.order_by(Length('theme').asc(), 'theme').all()
  if request.method == 'GET':
    form = AddThemeForm(request.GET or None)
  elif request.method == 'POST' and request.POST["action"] == "add":
    form = AddThemeForm(request.POST)
    if form.is_valid():
      inst = form.save(commit=False)
      inst.id = Themes.objects.all().aggregate(Max('id'))['id__max'] + 1
      inst.save()
      inst.save(using='cimetiere')
  elif request.method == 'POST' and request.POST["action"] == "edit":
    form = AddThemeForm()
    Themes.objects.filter(id=request.POST.get('ident')).update(
        titre=request.POST.get('titre'))

  return render(request, 'add_theme.html', {'form': form, 'themes_list': themes_list})


def deleteTheme(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Guides').exists()):
    return redirect(reverse(accueil))
  if request.method == 'POST':
    item = Themes.objects.get(id=request.POST.get('ident'))
    item.delete()
    return redirect(reverse(themes))

