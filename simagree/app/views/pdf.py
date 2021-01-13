from django.shortcuts import render, redirect
from django.http import FileResponse, Http404
from django.urls import reverse
from django.db.models import Q
from django.conf import settings

import os


# Create your views here.

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest, light_dbRequest
from .pdfgen import *
from .csvparser import *

########## Vues pour la gestion des pdf ##########

def impression(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))

  if request.method == "POST":
    selection = request.POST.getlist('remove')
    selection = [int(i) for i in selection]
    Identifiants.objects.filter(taxon__in=selection).update(a_imprimer=False)

  items = Nomenclature.objects.select_related('taxon').filter(
      Q(taxon__a_imprimer=True) & Q(codesyno=0)).all()
  return render(request, 'impression.html', {'shrooms': items})


def resetImpression(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))

  Identifiants.objects.filter(a_imprimer=True).update(a_imprimer=False)
  return redirect(reverse(impression))


def send_file(request, tax, type_fiche):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if type_fiche == "systematique":
    if not (request.user.groups.filter(name='Administrateurs').exists()):
      return redirect(reverse(accueil))
  else:
    if not (request.user.groups.filter(name='Guides').exists()):
      return redirect(reverse(accueil))
  # Suppression des fiches si trop nombreuses dans le dossier
  dir_fiches = settings.BASE_DIR + '/app/pdf_assets/fiches/'
  try:
    files = next(os.walk(dir_fiches))[2]
  except:
    raise Http404()
  if len(files) > 20:
    for i in files:
      os.remove(dir_fiches + i)

  # Generation du pdf
  # Objet
  item = Nomenclature.objects.select_related('taxon').filter(Q(taxon=tax) & Q(codesyno=0)).values(
      'taxon__fiche',
      'genre',
      'espece',
      'variete',
      'taxon__noms',
      'forme',
      'taxon__comestible',
      'taxon__notes',
      'taxon__ecologie',
      'taxon__theme1',
      'taxon__theme2',
      'taxon__theme3',
      'taxon__theme4',
      'taxon_id'
  )[0]

  vars = {}

  usuel = Nomenclature.objects.filter(Q(taxon=tax) & Q(
      codesyno=3)).values('genre', 'espece', 'variete', 'forme')

  if len(usuel) > 0:
    try:
      vars['usuel_genre'] = usuel[0]['genre']
      vars['usuel_espece'] = usuel[0]['espece']
      vars['usuel_variete'] = none2string(usuel[0]['variete'])
      vars['usuel_forme'] = none2string(usuel[0]['forme'])
    except:
      raise Http404()

  try:
    vars['taxon'] = str(item['taxon_id'])
    vars['fiche'] = none2string(item['taxon__fiche'])
    vars['genre'] = item['genre']
    vars['espece'] = item['espece']
    vars['variete'] = none2string(item['variete'])
    vars['forme'] = none2string(item['forme'])
    vars['noms'] = none2string(item['taxon__noms'])
    vars['comestibilite'] = none2string(item['taxon__comestible'])
    vars['obs'] = [none2string(item['taxon__notes']),
                   none2string(item['taxon__ecologie'])]
    fullpath = dir_fiches + none2string(item['taxon__fiche']) + '.pdf'
  except Exception as e:
    raise Http404()
  try:
    if type_fiche == "systematique":
      # Présence d'un thème ?
      has_theme = [item['taxon__theme1'], item['taxon__theme2'],
                   item['taxon__theme3'], item['taxon__theme4']]
      has_theme = not (has_theme.count(None) == len(has_theme))
      if has_theme:
        vars['theme'] = 'Th'
      generateFiche(fullpath, vars)
    else:
      vars['theme_code'] = type_fiche
      titre = Themes.objects.get(theme=type_fiche).titre
      vars['theme_titre'] = none2string(titre)
      generateFicheTheme(fullpath, vars)
    res = FileResponse(open(fullpath, 'rb'), content_type='application/pdf')
    #res['Content-Disposition'] = 'attachment; filename=' + vars['fiche']
    return res
  except FileNotFoundError:
    raise Http404()


def pdf_bulk(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  # Suppression des fiches si trop nombreuses dans le dossier
  dir_fiches = settings.BASE_DIR + '/app/pdf_assets/fiches/'
  try:
    files = next(os.walk(dir_fiches))[2]
  except:
    raise Http404()
  if len(files) > 20:
    for i in files:
      os.remove(dir_fiches + i)

  liste_fiches = [str(
      k['fiche']) + '.pdf' for k in Identifiants.objects.filter(a_imprimer=True).values('fiche')]
  items = Nomenclature.objects.select_related('taxon').filter(Q(taxon__a_imprimer=True) & Q(codesyno=0)).values(
      'taxon__fiche',
      'genre',
      'espece',
      'variete',
      'taxon__noms',
      'forme',
      'taxon__comestible',
      'taxon__notes',
      'taxon__ecologie',
      'taxon__theme1',
      'taxon__theme2',
      'taxon__theme3',
      'taxon__theme4',
      'taxon_id'
  )

  for i in items:
    vars = {}
    usuel = Nomenclature.objects.filter(Q(taxon=i['taxon_id']) & Q(
        codesyno=3)).values('genre', 'espece', 'variete', 'forme')

    if len(usuel) > 0:
      try:
        vars['usuel_genre'] = usuel[0]['genre']
        vars['usuel_espece'] = usuel[0]['espece']
        vars['usuel_variete'] = none2string(usuel[0]['variete'])
        vars['usuel_forme'] = none2string(usuel[0]['forme'])
      except:
        raise Http404()

    try:
      vars['taxon'] = str(i['taxon_id'])
      vars['fiche'] = none2string(i['taxon__fiche'])
      vars['genre'] = i['genre']
      vars['espece'] = i['espece']
      vars['variete'] = none2string(i['variete'])
      vars['forme'] = none2string(i['forme'])
      vars['noms'] = none2string(i['taxon__noms'])
      vars['comestibilite'] = none2string(i['taxon__comestible'])
      vars['obs'] = [none2string(i['taxon__notes']),
                     none2string(i['taxon__ecologie'])]
      fullpath = dir_fiches + none2string(i['taxon__fiche']) + '.pdf'
    except Exception as e:
      raise Http404()

    # Présence d'un thème ?
    has_theme = [i['taxon__theme1'], i['taxon__theme2'],
                 i['taxon__theme3'], i['taxon__theme4']]
    has_theme = not (has_theme.count(None) == len(has_theme))
    if has_theme:
      vars['theme'] = 'Th'
    generateFiche(fullpath, vars)
  bulk_pdf(liste_fiches, dir_fiches)
  res_file = open(settings.BASE_DIR + '/app/pdf_assets/fiches.pdf', 'rb')
  res = FileResponse(res_file, content_type='application/pdf')
  res['Content-Disposition'] = 'attachment; filename=fiches.pdf'
  return res