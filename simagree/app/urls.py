"""simagree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.accueil, name = 'home'),
    url(r'about/$', views.about, name = 'about'),
    url(r'^search/$', views.search, name = 'search'),
    url(r'^add_complete/$', views.add, name = 'add'),
    url(r'^add_partial/$', views.addPartial, name = 'addPart'),
    url(r'^details/(?P<id_item>[0-9]+)/$', views.details, name = 'details'),
    url(r'^delete/$', views.deleteConfirm, name = 'delete'),
    url(r'^delete_tax/$', views.deleteTaxon, name = 'delete-tax'),
    url(r'^modify/(?P<id>[0-9]+)/$', views.modify, name = 'modify'),
    url(r'^modify_tax/(?P<tax>[0-9]+)/$', views.modifyTaxon, name = 'modify-tax'),
    url(r'^modify_notes_eco/(?P<tax>[0-9]+)/$', views.modifyNotesEco, name = 'modify-noteseco'),
    url(r'^login/$', views.connexion, name = 'login'),
    url(r'^logout/$', views.deconnexion, name = 'logout'),
    url(r'^themes/$', views.themes, name = 'themes'),
    url(r'^deletetheme/$', views.deleteTheme, name = 'themes_del'),
    url(r'^file/(?P<tax>[0-9]+)/(?P<type_fiche>.+)/$', views.send_file, name = 'sendfile'),
    #url(r'^listes/edit/(?P<id_liste>[0-9]+)/$', views.editList, name = 'editList'),
    #url(r'^listes/$', views.showLists, name = 'showLists'),
    #url(r'^liste_details/(?P<id_liste>[0-9]+)/$', views.detailsList, name = 'detailsList'),
    url(r'^export/identifiants/$', views.csvIdent, name = 'export-ident'),
    url(r'^export/nomenclature/$', views.csvNomenc, name = 'export-nomenc'),
    url(r'^import_export/$', views.upload_csv, name = 'imp-exp'),
    url(r'^deleted/$', views.cimetiere, name = 'cimetiere'),
    url(r'^restore/(?P<tax>[0-9]+)/$', views.restoreTaxon, name = 'restore-tax'),
    url(r'^defdelete/$', views.definitiveDelete, name = 'delete-cimetiere'),
    url(r'^impression/$', views.impression, name = 'impression'),
    url(r'^impression/reset/$', views.resetImpression, name = 'reset-impression'),
    url(r'^bulkpdf/$', views.pdf_bulk, name='pdf-bulk')
]
