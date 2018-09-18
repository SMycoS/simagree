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
import PyPDF2

import datetime
import time
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
    marginX = 10
    marginY = 10
    cnv = canvas.Canvas(pdf_filename, pagesize = size, verbosity = 1) # 115 x 85 mm

    # Bordure pour le massicot
    cnv.rect(0,0, sizeX, sizeY, stroke = 1, fill = 0)

    # Styles pour les paragraphes
    styleSheet = getSampleStyleSheet()
    style = styleSheet['BodyText']
    style_obs = ParagraphStyle(name = 'Obs', fontSize = 9, leading=9, fontName = 'Helvetica-Oblique')
    style_usuel = ParagraphStyle(name = 'SynoUsuel', fontSize = 12, alignment = 1, leading = 12)

    # Genre - Espece
    style_nomenc = ParagraphStyle(name = 'Nomenclature', fontSize = 18, alignment = 1, fontName = 'Helvetica-Bold', leading = 22 )
    # Variete - Forme
    style_nomenc_bis = ParagraphStyle(name = 'NomenclatureBis', fontSize = 14, alignment = 1, leading = 11, fontName = 'Helvetica-Bold')
    # Noms
    style_noms = ParagraphStyle(name = 'Noms', fontSize = 12, leading=12, fontName = 'Helvetica-Bold')
    
    # Theme
    if 'theme' in vars.keys():
        cnv.drawString(marginX, sizeY - (marginY + 10), vars['theme'])

    # Numero de fiche
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 10), vars['fiche'])

    # Rectangle supérieur
    cnv.setLineWidth(2)
    frame_top = Frame(0 + marginX, midY + (4.5 * marginY) + 5, sizeX - (2 * marginX), sizeY / 5, showBoundary = 1,
        topPadding=2,
        leftPadding=2,
        rightPadding=2,
        bottomPadding=2)
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
        frameW = sizeX * 0.65
        frameH = marginY * 7
        frame_noms = Frame(marginX, midY  - 4.5 * marginY, frameW, frameH, showBoundary = 0)
        noms = []
        for nom in vars['noms'].splitlines():
            if nom != "":
                noms.append(Paragraph(nom, style_noms))

        noms_inframe = KeepInFrame(frameW, frameH, noms)
        frame_noms.addFromList([noms_inframe], cnv)
    
    # Synonyme usuel
    if 'usuel_genre' in vars.keys():
        frameW = 0.66 * sizeX
        frameH = marginY * 3.5
        frame_syno = Frame(0.165 * sizeX, midY + 2 * marginY, frameW, frameH, showBoundary = 0)
        if vars['usuel_variete'] != "":
            varfor_str = ' var. ' + vars['usuel_variete']
        elif vars['usuel_forme'] != "":
            varfor_str = ' f. ' + vars['usuel_forme']
        else:
            varfor_str = ''
        ustr = '( = ' + vars['usuel_genre'] + ' ' + vars['usuel_espece'] + varfor_str + ' )'
        usuel = [Paragraph(ustr, style_usuel)]

        usuel_inframe = KeepInFrame(frameW, frameH, usuel)
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
    frameW = sizeX - (2 * marginX)
    frameH = sizeY / 5
    frame_obs = Frame(0 + marginX, 5 + marginY, frameW, frameH, showBoundary=1, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)

    # Observations
    if 'obs' in vars.keys():
        observations = [Paragraph(vars['obs'][0], style_obs), Paragraph(vars['obs'][1], style_obs)]
        obs_inframe = KeepInFrame(frameW, frameH, observations)
        frame_obs.addFromList([obs_inframe], cnv)

    # Copyright
    cnv.setFont('Helvetica', 8)
    year = str(datetime.datetime.now().year)
    cnv.drawRightString(sizeX - marginX, marginY - 5, '©SMS ' + year)

    # Code Barre (standard code39)
    barcode=code39.Standard39(vars['taxon'], barWidth=0.5*mm,barHeight=3.5*mm, checksum = 0)
    barcode.drawOn(cnv, 10 , 3)
    cnv.showPage()
    cnv.save()

# Génère une fiche thématique
def generateFicheTheme(pdf_filename, vars, size = (325.984, 240.945)):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 10
    marginY = 10
    cnv = canvas.Canvas(pdf_filename, pagesize = size, verbosity = 1) # 115 x 85 mm
    style_eco = ParagraphStyle(name = 'ObsEco', fontSize = 10, leading=10, fontName = 'Helvetica-Oblique')
    style_notes = ParagraphStyle(name = 'ObsNotes', fontSize = 9, leading=9, fontName = 'Helvetica-Bold')
    style_titre = ParagraphStyle(
        name = 'ThemeTitre', 
        fontName = 'Helvetica-Bold',
        fontSize = 14,
        alignment = 1,
        textColor = colors.Color(239/255, 239/255, 0,1)
        
    )
    style_nomenc = ParagraphStyle(name = 'Nomenc', fontName = 'Helvetica-BoldOblique', fontSize=12)
    style_nomenc_bis = ParagraphStyle(name = 'Nomenc', fontName = 'Helvetica-Oblique', fontSize = 10)
    style_noms = ParagraphStyle(name = 'Noms', fontSize = 16, alignment = 1, fontName = 'Helvetica-Bold', leading = 16)

    
    # Rectangle du haut
    cnv.setStrokeColorRGB(80 / 255, 80 / 255, 80 / 255)
    cnv.setLineWidth(2)
    cnv.setFillColorRGB(80 / 255,80 / 255,80 / 255)
    cnv.rect(0, sizeY - (10 * mm), sizeX, 10 * mm, fill = True)

    # Bordure pour le massicot
    cnv.setStrokeColorRGB(0, 0, 0)
    cnv.setLineWidth(1)
    cnv.rect(0,0, sizeX, sizeY, stroke = 1, fill = 0)
    
    # Numero de fiche
    cnv.setStrokeColorRGB(0,0,0)
    cnv.setFillColorRGB(1,1,1)
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 10), vars['fiche'])

    # Theme
    cnv.drawString(marginX, sizeY - (marginY + 10), vars['theme_code'])
    cnv.setFillColorRGB(0, 0, 0)
    frameW = sizeX - (9 * marginX)
    frameH = marginY * 2.5
    frame_titre = Frame(4.5 * marginX, sizeY - marginY * 2.7, frameW, frameH, showBoundary = 0, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)
    titre = [Paragraph(vars['theme_titre'], style_titre)]
    titre_inframe = KeepInFrame(frameW, frameH, titre)
    frame_titre.addFromList([titre_inframe], cnv)
    

    # Genre et Espece
    cnv.setFillColorRGB(0,0,0)
    frameW = sizeX /2
    frameH = 5.5 * marginY
    frame_nomenc = Frame(marginX * 0.6, sizeY - (10 * mm) - frameH, frameW , frameH, showBoundary = 0, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)
    nomenc = []
    
    # Genre et Espece
    genre_esp = vars['genre'] + ' ' + vars['espece']
    if vars['variete'] != "":
        genre_esp += 'var. ' + vars['variete']
    elif vars['forme'] != "":
        genre_esp += 'f. ' + vars['forme']

    nomenc.append(Paragraph(genre_esp, style_nomenc))

    if 'usuel_genre' in vars.keys():
        nomenc.append(Paragraph('( = ' + vars['usuel_genre'] + ' ' + vars['usuel_espece'] + ' ) ', style_nomenc_bis))
        if vars['usuel_variete'] != "":
            nomenc.append(Paragraph('var. ' + vars['usuel_variete'], style_nomenc_bis))
        elif vars['usuel_forme'] != "":
            nomenc.append(Paragraph('f. ' + vars['usuel_forme'], style_nomenc_bis))

    nomenc_inframe = KeepInFrame(frameW, frameH, nomenc)
    frame_nomenc.addFromList([nomenc_inframe], cnv)

    cnv.setFont('Helvetica', 11)


    # Noms usuels
    if 'noms' in vars.keys() and vars['noms'] != "":
        frameW = sizeX * 0.75
        frameH = marginY * 6
        frame_noms = Frame(marginX, midY  - 3 * marginY, frameW, frameH, showBoundary = 0, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)
        noms = []
        for nom in vars['noms'].splitlines():
            if nom != "":
                noms.append(Paragraph(nom, style_noms))
        noms_inframe = KeepInFrame(frameW, frameH, noms)
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
    frame_obs = Frame(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, showBoundary=1, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)

    # Observations
    if 'obs' in vars.keys():
        notes = [Paragraph(vars['obs'][0], style_notes)]
        eco = [Paragraph(vars['obs'][1], style_eco)]
        frame_eco = Frame(0 + marginX, 5 + (1 * marginY) + sizeY / 6, sizeX - (2 * marginX), 2.6 * marginY, showBoundary=0, leftPadding=2, topPadding=2, rightPadding=2, bottomPadding=2)
        notes_inframe = KeepInFrame(sizeX - (2 * marginX), sizeY / 6, notes)
        eco_inframe = KeepInFrame(sizeX - (2 * marginX), 2.6 * marginY, eco)
        frame_obs.addFromList([notes_inframe], cnv)
        frame_eco.addFromList([eco_inframe], cnv)

    # Copyright
    cnv.setFont('Helvetica', 8)
    year = str(datetime.datetime.now().year)
    cnv.drawRightString(sizeX - marginX, marginY - 5, '©SMS ' + year)

    # Code Barre (standard code39)
    barcode=code39.Standard39(vars['taxon'], barWidth=0.5*mm,barHeight=3.5*mm, checksum = 0)
    barcode.drawOn(cnv, 10 , 3)

    cnv.showPage()
    cnv.save()

def bulk_pdf(fiche_list, rep):
    blank_page_path = settings.BASE_DIR + '/app/pdf_assets/blankA4.pdf'
    output_file = open(settings.BASE_DIR + '/app/pdf_assets/fiches.pdf', 'wb')
    write_pdf = PyPDF2.PdfFileWriter()
    # On ouvre un pdf blanc
    base = open(blank_page_path, 'rb')
    offset_x = 150
    offset_y = 270

    liste_size = len(fiche_list)
    reste = liste_size % 3
    reste_list = []

    for cpt,fiche in enumerate(fiche_list):
        if cpt < liste_size - reste:
            iteration = cpt % 3
            # parcours 3 par 3
            if iteration == 0:
                input_pdf = PyPDF2.PdfFileReader(base)
                output_pdf = input_pdf.getPage(0)
                f1 = open(rep + fiche_list[cpt], 'rb')
                f2 = open(rep + fiche_list[cpt + 1], 'rb')
                f3 = open(rep + fiche_list[cpt + 2], 'rb')

            for i, f in enumerate([f1, f2, f3]):
                f_pdf = PyPDF2.PdfFileReader(f).getPage(0)
                output_pdf.mergeTranslatedPage(f_pdf, offset_x, 30 + i * offset_y, expand=True)

            # add second page to first one
            if iteration == 0:
                write_pdf.addPage(output_pdf)

    
    
    if reste != 0:
        input_pdf = PyPDF2.PdfFileReader(base)
        output_pdf = input_pdf.getPage(0)
        if reste == 1:
            fr1 = open(rep + fiche_list[liste_size - 1], 'rb')
            f_pdf = PyPDF2.PdfFileReader(fr1).getPage(0)
            output_pdf.mergeTranslatedPage(f_pdf, offset_x, 30 +  offset_y, expand=True)
        elif reste == 2:
            fr1 = open(rep + fiche_list[liste_size - 1], 'rb')
            f_pdf = PyPDF2.PdfFileReader(fr1).getPage(0)
            output_pdf.mergeTranslatedPage(f_pdf, offset_x, 30 + offset_y, expand=True)
            fr2 = open(rep + fiche_list[liste_size - 2], 'rb')
            f_pdf = PyPDF2.PdfFileReader(fr2).getPage(0)
            output_pdf.mergeTranslatedPage(f_pdf, offset_x, 30 + 2 * offset_y, expand=True)


        write_pdf.addPage(output_pdf)
    
    base.close()
    write_pdf.write(output_file)