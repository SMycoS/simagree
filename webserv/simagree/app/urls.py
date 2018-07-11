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
    url(r'^search/$', views.search, name = 'search'),
    url(r'^add_complete/$', views.add, name = 'add'),
    url(r'add_partial/$', views.addPartial, name = 'addPart'),
    url(r'^details/(?P<tax>[0-9]+)/$', views.details, name = 'details'),
    url(r'^delete/$', views.deleteConfirm, name = 'delete'),
    url(r'^modify/(?P<id>[0-9]+)/$', views.modify, name = 'modify'),
    url(r'^login/$', views.connexion, name = 'login'),
    url(r'^logout/$', views.deconnexion, name = 'logout'),
    url(r'^themes/$', views.themes, name = 'themes'),
    url(r'^deletetheme/$', views.deleteTheme, name = 'themes_del'),
]
