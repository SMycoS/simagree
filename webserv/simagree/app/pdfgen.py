# ReportLab utilise les points comme unité de base
# 1 px = 0.75 pt
# 

from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.barcode import code39
from reportlab.lib.units import mm, cm
from django.conf import settings

import datetime
from io import StringIO, BytesIO

# Génère une fiche au format PDF
# Prend un doublet (size) en argument : taille en points
# un nom de fichier
# et un dictionnaire de valeurs (vars)
def generateFiche(pdf_filename, vars, size = (115*mm, 85*mm)):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 20
    marginY = 20
    cnv = canvas.Canvas(pdf_filename, pagesize = size, verbosity = 1) # 115 x 85 mm

    # Styles pour les paragraphes
    styleSheet = getSampleStyleSheet()
    style = styleSheet['BodyText']
    style_obs = ParagraphStyle(name = 'Obs', fontSize = 6)
    style_usuel = ParagraphStyle(name = 'SynoUsuel', fontSize = 10, alignment = 1, leading = 10)

    # Genre - Espece
    style_nomenc = ParagraphStyle(name = 'Nomenclature', fontSize = 16, alignment = 1, fontName = 'Helvetica-Bold', leading = 22 )
    # Variete - Forme
    style_nomenc_bis = ParagraphStyle(name = 'NomenclatureBis', fontSize = 11, alignment = 1, leading = 11)
    # Noms
    style_noms = ParagraphStyle(name = 'Noms', fontSize = 10)
    print(style_usuel)
    
    # Theme
    if 'theme' in vars.keys():
        cnv.drawString(marginX, sizeY - (marginY + 5), vars['theme'])

    # Numero de fiche (Obligatoire si on génère une fiche)
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 5), vars['fiche'])

    # Rectangle supérieur
    cnv.setLineWidth(2)
    frame_top = Frame(0 + marginX, midY + (1.5 * marginY) + 5, sizeX - (2 * marginX), sizeY / 5, showBoundary = 1)
    nomenc = []

    # Genre et Espece
    nomenc.append(Paragraph(vars['genre'] + ' ' + vars['espece'], style_nomenc))

    # Variete et Forme
    if vars['variete'] != "":
        nomenc.append(Paragraph('var. ' + vars['variete'], style_nomenc_bis))
    elif vars['forme'] != "":
        nomenc.append(Paragraph('f. ' + vars['forme'], style_nomenc_bis))


    nomenc_inframe = KeepInFrame(sizeX - (2 * marginX), sizeY / 5, nomenc)
    frame_top.addFromList([nomenc_inframe], cnv)
    cnv.setLineWidth(1)

    # Noms
    if 'noms' in vars.keys() and vars['noms'] != "":
        frame_noms = Frame(marginX, midY  - 2.5 * marginY, sizeX * 0.65 , marginY * 3, showBoundary = 0)
        noms = []
        for nom in vars['noms'].splitlines():
            if nom != "":
                noms.append(Paragraph(nom, style_noms))

        noms_inframe = KeepInFrame(sizeX * 0.65 , marginY * 3.7, noms)
        frame_noms.addFromList([noms_inframe], cnv)
    
    # Synonyme usuel
    if 'usuel_genre' in vars.keys():
        frame_syno = Frame(sizeX / 4, midY + 0.5 * marginY, sizeX / 2,  marginY * 1.2, showBoundary = 0)
        if vars['usuel_variete'] != "":
            varfor_str = ' var. ' + vars['usuel_variete']
        elif vars['usuel_forme'] != "":
            varfor_str = ' f. ' + vars['usuel_forme']
        else:
            varfor_str = ''
        ustr = '( = ' + vars['usuel_genre'] + ' ' + vars['usuel_espece'] + varfor_str + ' )'
        usuel = [Paragraph(ustr, style_usuel)]

        usuel_inframe = KeepInFrame(sizeX / 2,  marginY * 1.2, usuel)
        frame_syno.addFromList([usuel_inframe], cnv)


    # Texte comestibilite
    if 'comestibilite' in vars.keys() and vars['comestibilite'] != "":
        assets_path = settings.BASE_DIR + '/app/pdf_assets/'
        if (vars['comestibilite'] == 'C'):
            com_txt = 'Comestible'
            com_img = assets_path + 'Comest.bmp'
        elif (vars['comestibilite'] == 'NC'):
            com_txt = 'Non Comestible'
            com_img = assets_path + 'NonCom.bmp'
        elif (vars['comestibilite'] == 'T'):
            com_txt = 'Toxique'
            com_img = assets_path + 'Toxique.bmp'
        else:
            com_txt = 'Mortel'
            com_img = assets_path + 'Mortel.bmp'

        img_width = 138.75 / 2.5
        img_height = 131.25 / 2.5
        
        cnv.drawImage(com_img, sizeX - marginX - img_width, midY - (1.5 * marginY), width = img_width, height= img_width)
        cnv.drawRightString(sizeX - marginX, midY - (2 * marginY) - 5, com_txt)
    
    # Rectangle du bas
    cnv.setLineWidth(1)
    frame_obs = Frame(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, showBoundary=1)

    # Observations
    if 'obs' in vars.keys():
        observations = [Paragraph(vars['obs'][0], style_obs), Paragraph(vars['obs'][1], style_obs)]
        obs_inframe = KeepInFrame(sizeX - (2 * marginX), sizeY / 6, observations)
        frame_obs.addFromList([obs_inframe], cnv)

    # Copyright
    cnv.setFont('Helvetica', 8)
    year = str(datetime.datetime.now().year)
    cnv.drawCentredString(midX, marginY - 10, '©SMS ' + year + ' - Société Mycologique de Strasbourg')

    # Code Barre (standard code39)
    if len(vars['taxon']) > 8:
        barW = 0.1 * mm
    else:
        barW = 0.15*mm
    barcode=code39.Standard39(vars['taxon'], barWidth=barW,barHeight=5*mm)
    barcode.drawOn(cnv, sizeX * 0.73, 5)

    cnv.save()

# Génère une fiche thématique
def generateFicheTheme(pdf_filename, vars, size = (325.984, 240.945)):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 20
    marginY = 20
    cnv = canvas.Canvas(pdf_filename, pagesize = size, verbosity = 1) # 115 x 85 mm
    style_eco = ParagraphStyle(name = 'ObsEco', fontSize = 6, fontName = 'Helvetica-Oblique')
    style_notes = ParagraphStyle(name = 'ObsNotes', fontSize = 6, fontName = 'Helvetica-Bold')
    style_titre = ParagraphStyle(
        name = 'ThemeTitre', 
        fontName = 'Helvetica-Bold',
        fontSize = 14,
        alignment = 1,
        textColor = colors.Color(0,1,1,1)
        
    )
    style_nomenc = ParagraphStyle(name = 'Nomenc', fontName = 'Helvetica-BoldOblique', )
    style_nomenc_bis = ParagraphStyle(name = 'Nomenc', fontName = 'Helvetica-Oblique', fontSize = 8)
    style_noms = ParagraphStyle(name = 'Noms', fontSize = 10, alignment = 1, fontName = 'Helvetica-Bold')

    # Rectangle du haut
    cnv.setStrokeColorRGB((133 / 255), (133 / 255), (133 / 255))
    cnv.setLineWidth(2)
    cnv.setFillColorRGB((133 / 255), (133 / 255), (133 / 255))
    cnv.rect(0, sizeY - (2 * marginY), sizeX, 2 * marginY, fill = True)
    
    # Numero de fiche
    cnv.setStrokeColorRGB(0,0,0)
    cnv.setFillColorRGB(1,1,1)
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 5), vars['fiche'])

    # Theme
    cnv.drawString(marginX, sizeY - (marginY + 5), vars['theme_code'])

    cnv.setFillColorRGB(0,1,1)
    frame_titre = Frame(3.5 * marginX, sizeY - marginY * 1.8, sizeX - 7 * marginX, marginY * 1.5, showBoundary = 0)
    titre = [Paragraph(vars['theme_titre'], style_titre)]
    titre_inframe = KeepInFrame(sizeX - 7 * marginX, marginY, titre)
    frame_titre.addFromList([titre_inframe], cnv)
    

    # Genre et Espece
    cnv.setFillColorRGB(0,0,0)
    frame_nomenc = Frame(marginX * 0.6, sizeY - (4.5 * marginY), sizeX /2 , 2.5 * marginY, showBoundary = 0)
    nomenc = []
    
    # Genre et Espece
    nomenc.append(Paragraph(vars['genre'] + ' ' + vars['espece'], style_nomenc))

    # Variete et Forme
    if vars['variete'] != "":
        nomenc.append(Paragraph(vars['variete'], style_nomenc_bis))
    elif vars['forme'] != "":
        nomenc.append(Paragraph(vars['forme'], style_nomenc_bis))
    if 'usuel_genre' in vars.keys():
        nomenc.append(Paragraph('( = ' + vars['usuel_genre'] + ' ' + vars['usuel_espece'] + ' ) ', style_nomenc_bis))
        if vars['usuel_variete'] != "":
            nomenc.append(Paragraph('var. ' + vars['usuel_variete'], style_nomenc_bis))
        elif vars['usuel_forme'] != "":
            nomenc.append(Paragraph('f. ' + vars['usuel_forme'], style_nomenc_bis))

    nomenc_inframe = KeepInFrame(sizeX / 2, 2 * marginY, nomenc)
    frame_nomenc.addFromList([nomenc_inframe], cnv)

    cnv.setFont('Helvetica', 11)


    # Noms usuels
    if 'noms' in vars.keys() and vars['noms'] != "":
        frame_noms = Frame(1.5 * marginX, midY  - 1.5 * marginY, sizeX * 0.65 , marginY * 3, showBoundary = 0)
        noms = []
        for nom in vars['noms'].splitlines():
            if nom != "":
                noms.append(Paragraph(nom, style_noms))
        noms_inframe = KeepInFrame(sizeX * 0.65 , marginY * 3.7, noms)
        frame_noms.addFromList([noms_inframe], cnv)


    # Texte comestibilite
    if 'comestibilite' in vars.keys() and vars['comestibilite'] != "":
        assets_path = settings.BASE_DIR + '/app/pdf_assets/'
        if (vars['comestibilite'] == 'C'):
            com_txt = 'Comestible'
            com_img = assets_path + 'Comest.bmp'
        elif (vars['comestibilite'] == 'NC'):
            com_txt = 'Non Comestible'
            com_img = assets_path + 'NonCom.bmp'
        elif (vars['comestibilite'] == 'T'):
            com_txt = 'Toxique'
            com_img = assets_path + 'Toxique.bmp'
        else:
            com_txt = 'Mortel'
            com_img = assets_path + 'Mortel.bmp'

        img_width = 138.75 / 2.5
        img_height = 131.25 / 2.5
        
        cnv.drawImage(com_img, sizeX - marginX - img_width, midY + (0.5 * marginY), width = img_width, height= img_width)
        cnv.drawRightString(sizeX - marginX, midY - (0 * marginY) - 5, com_txt)

    # Rectangle du bas
    cnv.setLineWidth(1)
    frame_obs = Frame(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, showBoundary=1)

    # Observations
    if 'obs' in vars.keys():
        notes = [Paragraph(vars['obs'][0], style_notes)]
        eco = [Paragraph(vars['obs'][1], style_eco)]
        frame_eco = Frame(0 + marginX, 5 + marginY + sizeY / 6, sizeX - (2 * marginX), 1.2 * marginY, showBoundary=0)
        notes_inframe = KeepInFrame(sizeX - (2 * marginX), sizeY / 6, notes)
        eco_inframe = KeepInFrame(sizeX - (2 * marginX), sizeY / 6, eco)
        frame_obs.addFromList([notes_inframe], cnv)
        frame_eco.addFromList([eco_inframe], cnv)

    # Copyright
    cnv.setFont('Helvetica', 8)
    year = str(datetime.datetime.now().year)
    cnv.drawCentredString(midX, marginY - 10, '©SMS ' + year + ' - Société Mycologique de Strasbourg')

    # Code Barre (standard code39)
    barcode=code39.Standard39(vars['taxon'],barWidth=0.5*mm,barHeight=8*mm)
    barcode.drawOn(cnv,sizeX * 0.75,5)


    cnv.save()
