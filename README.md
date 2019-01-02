# simagree
Base de données mycologique

Système d'Information Mycologique : Aide à la Gestion des REcoltes et des Expositions

## Lancer le serveur de développement

Il faut de préférence créer un environnement virtuel (python 3)

```bash
# dependances (si non installées)
pip install -r requirements.txt

# serveur
cd simagree
python manage.py runserver

# selon l'OS (ou la configuration du venv), il faut utiliser la commande python 3 au lieu de simplement python
```

## Dépendances

SIMAGREE utilise plusieurs dépendances externes (en plus de Django) comme des plugins jQuery, ...

* [jQuery](https://jquery.com/)
* [Bootstrap 4 (CSS et JS)](https://getbootstrap.com/)
* [Chosen](https://harvesthq.github.io/chosen/)
* [bootstrap-duallistbox](https://github.com/istvan-ujjmeszaros/bootstrap-duallistbox)
* [datepicker](https://github.com/fengyuanchen/datepicker)
* [PyPDF2](https://github.com/mstamy2/PyPDF2)
* [ReportLab](https://www.reportlab.com)

## Notes

Les paramètres sur le serveur hébergé en ligne sont différents de ceux du dépôt (notamment ce qui concerne le mode debug, la clé secrète et la gestion des cookies de session)
