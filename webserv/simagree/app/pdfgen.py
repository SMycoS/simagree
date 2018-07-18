# ReportLab utilise les points comme unité de base
# 1 px = 0.75 pt
# 

from reportlab.pdfgen import canvas

# Génère une fiche au format PDF
# Prend un doublet (size) en argument : taille en points
# un nom de fichier
# et un dictionnaire de valeurs (vars)
def generateFiche(pdf_filename, vars, size = (325.984, 240.945)):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 20
    marginY = 20
    cnv = canvas.Canvas(pdf_filename, pagesize = size, verbosity = 1) # 115 x 85 mm

    # Theme
    if 'theme' in vars.keys():
        cnv.drawString(marginX, sizeY - (marginY + 5), vars['theme'])

    # Numero de fiche (Obligatoire si on génère une fiche)
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 5), vars['fiche'])

    # Genre et Espece (Obligatoires dans la BDD)
    cnv.setFont('Helvetica-Bold', 16)
    cnv.drawCentredString(midX, sizeY - (3 * marginY) + 5, vars['genre'] + ' ' + vars['espece'])

    # Variete et Forme
    var_for = ''
    if 'variete' in vars.keys():
        var_for = vars['variete']
    if 'forme' in vars.keys():
        var_for += ' ' + vars['forme']
    cnv.setFont('Helvetica', 11)
    cnv.drawCentredString(midX, sizeY - (4 * marginY) + 5, var_for)

    # Rectangle du haut
    cnv.setLineWidth(2)
    cnv.rect(0 + marginX, midY + (1.5 * marginY) + 5, sizeX - (2 * marginX), sizeY / 5 , fill = False)

    # Noms usuels
    if 'noms' in vars.keys():
        cnv.drawString(marginX, midY + (0.5 * marginY), vars['noms'])

    # Texte comestibilite
    if 'comestibilite' in vars.keys():
        if (vars['comestibilite'] == 'C'):
            com_txt = 'Comestible'
            com_img = 'pdf_assets/Comest.bmp'
        elif (vars['comestibilite'] == 'NC'):
            com_txt = 'Non Comestible'
            com_img = 'pdf_assets/NonCom.bmp'
        elif (vars['comestibilite'] == 'T'):
            com_txt = 'Toxique'
            com_img = 'pdf_assets/Toxique.bmp'
        else:
            com_txt = 'Mortel'
            com_img = 'pdf_assets/Mortel.bmp'

        img_width = 138.75 / 2.5
        img_height = 131.25 / 2.5
        
        cnv.drawImage(com_img, sizeX - marginX - img_width, midY - (1.5 * marginY), width = img_width, height= img_width)
        cnv.drawRightString(sizeX - marginX, midY - (2 * marginY) - 5, com_txt)

    # Observations
    if 'obs' in vars.keys():
        cnv.setFont('Helvetica', 10)
        cnv.drawString(marginX + 10, (sizeX / 6) - 5, vars['obs'])

    # Rectangle du bas
    cnv.setLineWidth(1)
    cnv.rect(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, fill = False)

    # Copyright
    cnv.setFont('Helvetica', 8)
    cnv.drawCentredString(midX, marginY - 10, 'Copyright © Société Mycologique de Strasbourg')


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
    cnv.drawString(marginX, sizeY - (marginY + 5), 'Theme')
    cnv.setFillColorRGB(0,1,1)
    cnv.setFont('Helvetica-Bold', 14)
    cnv.drawCentredString(midX, sizeY - (marginY + 5), vars['theme']) 

    # Genre et Espece
    cnv.setFillColorRGB(0,0,0)
    cnv.drawString(marginX, sizeY - (3 * marginY), vars['genre'] + ' ' + vars['espece'])

    # Variete et Forme
    var_for = ''
    if 'variete' in vars.keys():
        var_for = vars['variete']
    if 'forme' in vars.keys():
        var_for += ' ' + vars['forme']
    cnv.setFont('Helvetica', 11)
    cnv.drawString(marginX, sizeY - (4 * marginY), var_for)


    # Noms usuels
    if 'noms' in vars.keys():
        cnv.drawString(2 * marginX, midY + (0.5 * marginY), vars['noms'])

    # Texte comestibilite
    if 'comestibilite' in vars.keys():
        if (vars['comestibilite'] == 'C'):
            com_txt = 'Comestible'
            com_img = 'pdf_assets/Comest.bmp'
        elif (vars['comestibilite'] == 'NC'):
            com_txt = 'Non Comestible'
            com_img = 'pdf_assets/NonCom.bmp'
        elif (vars['comestibilite'] == 'T'):
            com_txt = 'Toxique'
            com_img = 'pdf_assets/Toxique.bmp'
        else:
            com_txt = 'Mortel'
            com_img = 'pdf_assets/Mortel.bmp'

        img_width = 138.75 / 2.5
        img_height = 131.25 / 2.5
        
        cnv.drawImage(com_img, sizeX - marginX - img_width, midY + (0.5 * marginY), width = img_width, height= img_width)
        cnv.drawRightString(sizeX - marginX, midY - (0 * marginY) - 5, com_txt)

    # Observations
    if 'obs' in vars.keys():
        cnv.setFont('Helvetica', 10)
        cnv.drawString(marginX + 10, (sizeX / 6) - 5, vars['obs'])

    # Rectangle du bas
    cnv.setLineWidth(1)
    cnv.rect(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, fill = False)

    # Copyright
    cnv.setFont('Helvetica', 8)
    cnv.drawCentredString(midX, marginY - 10, 'Copyright © Société Mycologique de Strasbourg')


    cnv.save()
