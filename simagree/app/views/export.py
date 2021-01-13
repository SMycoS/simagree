from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.contrib import messages

import datetime
import codecs
from io import StringIO

from .models import Identifiants, Themes, Nomenclature
from .forms import *
from .searchparser import dbRequest, light_dbRequest
from .pdfgen import *
from .csvparser import *

########## Vues pour l'import / export de la base en csv ##########


def csvIdent(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  # Création d'une reponse au format csv
  response = HttpResponse(content_type='text/csv')
  filename = datetime.datetime.now().strftime('"SMS_Identifiants_%d-%m-%Y.csv"')
  response['Content-Disposition'] = 'attachment; filename=' + filename
  response.write(codecs.BOM_UTF8)
  # Création du header
  csv_header = (
      'Taxon',
      'SMS',
      'Comestibilité',
      'Fiche',
      'A imprimer',
      'Apparition',
      'Noms usuels',
      'Notes',
      'Ecologie',
      'Thème 1',
      'Thème 2',
      'Thème 3',
      'Thème 4',
      'Iconographie 1',
      'Iconographie 2',
      'Iconographie 3',
      'Numéro herbier'
  )
  # Chargement du fichier templace
  template = loader.get_template('csv_identifiants_template.txt')

  # Objet
  c = {
      'header': csv_header,
      'data': Identifiants.objects.all()
  }
  response.write(template.render(c))
  return response


def csvNomenc(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  # Création d'une reponse au format csv
  response = HttpResponse(content_type='text/csv')
  filename = datetime.datetime.now().strftime('"SMS_Nomenclature_%d-%m-%Y.csv"')
  response['Content-Disposition'] = 'attachment; filename=' + filename
  response.write(codecs.BOM_UTF8)
  # Création du header
  csv_header = (
      'Taxon',
      'Code Synonyme',
      'Genre',
      'Espèce',
      'Variété',
      'Forme',
      'Autorité',
      'Biliographie 1',
      'Bibliographie 2',
      'Bibliographie 3',
      'Tri MOSER',
      'Date'
  )
  # Chargement du fichier templace
  template = loader.get_template('csv_nomenclature_template.txt')

  # Objet
  c = {
      'header': csv_header,
      'data': Nomenclature.objects.all().order_by('taxon_id', 'codesyno')
  }
  response.write(template.render(c))
  return response


def upload_csv(request):
  if not request.user.is_authenticated:
    return redirect(reverse(connexion))
  if not (request.user.groups.filter(name='Administrateurs').exists()):
    return redirect(reverse(accueil))
  if "GET" == request.method:
    form = UploadFileForm()
    return render(request, "import_export.html", {'form': form})
  # if not GET, then proceed
  form = UploadFileForm(request.POST, request.FILES)
  if form.is_valid():
    if form.cleaned_data['csv_id']:
      up_file_id = request.FILES['csv_id']
      csv_file_id = StringIO(up_file_id.read().decode('UTF-8'))
      if replaceIdentifiants(csv_file_id):
        messages.success(
            request, 'La base Identifiants a bien été mise à jour.')
      else:
        messages.error(
            request, "Une erreur est survenue lors de l'import de la base Identifiants.")
        return HttpResponseRedirect(reverse("imp-exp"))
    if form.cleaned_data['csv_classification']:
      up_file_cla = request.FILES['csv_classification']
      csv_file_cla = StringIO(up_file_cla.read().decode('UTF-8'))
      if replaceClassification(csv_file_cla):
        messages.success(
            request, 'La base Classification a bien été mise à jour.')
      else:
        messages.error(
            request, "Une erreur est survenue lors de l'import de la base Classification.")
        return HttpResponseRedirect(reverse("imp-exp"))
    if form.cleaned_data['csv_nom']:
      up_file_nom = request.FILES['csv_nom']
      csv_file_nom = StringIO(up_file_nom.read().decode('UTF-8'))
      if replaceNomenclature(csv_file_nom):
        messages.success(
            request, 'La base Nomenclature a bien été mise à jour.')
      else:
        messages.error(
            request, "Une erreur est survenue lors de l'import de la base Nomenclature.")
        return HttpResponseRedirect(reverse("imp-exp"))
  return HttpResponseRedirect(reverse("imp-exp"))