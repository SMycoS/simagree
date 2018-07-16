# ReportLab utilise les points comme unité de base
# 1 px = 0.75 pt
# 

from reportlab.pdfgen import canvas

def generateFiche(size, com):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 20
    marginY = 20
    print(midX, midY)
    cnv = canvas.Canvas('test.pdf', pagesize = size, verbosity = 1) # 115 x 85 mm

    # Theme
    cnv.drawString(marginX, sizeY - (marginY + 5), 'APX 3')

    # Numero de fiche
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 5), 'Fiche #2458')

    # Genre et Espece
    cnv.setFont('Helvetica', 16)
    cnv.drawCentredString(midX, sizeY - (3 * marginY) + 5, 'Foo Bar')

    # Variete et Forme
    cnv.setFont('Helvetica', 11)
    cnv.drawCentredString(midX, sizeY - (4 * marginY) + 5, 'Variété / Forme')

    # Rectangle du haut
    cnv.setLineWidth(2)
    cnv.rect(0 + marginX, midY + (1.5 * marginY) + 5, sizeX - (2 * marginX), sizeY / 5 , fill = False)

    # Noms usuels
    cnv.drawString(marginX, midY + (0.5 * marginY), 'Noms usuels, ...')

    # Texte comestibilite
    if (com == 'C'):
        com_txt = 'Comestible'
        com_img = 'pdf_assets/Comest.bmp'
    elif (com == 'NC'):
        com_txt = 'Non Comestible'
        com_img = 'NonCom.bmp'
    elif (com == 'T'):
        com_txt = 'Toxique'
        com_img = 'Toxique.bmp'
    else:
        com_txt = 'Mortel'
        com_img = 'Mortel.bmp'

    img_width = 138.75 / 2.5
    img_height = 131.25 / 2.5
    
    cnv.drawImage(com_img, sizeX - marginX - img_width, midY - (1.5 * marginY), width = img_width, height= img_width)
    cnv.drawRightString(sizeX - marginX, midY - (2 * marginY) - 5, com_txt)

    # Observations
    cnv.setFont('Helvetica', 10)
    cnv.drawString(marginX + 10, (sizeX / 6) - 5, 'Blablablablablabla . . .')

    # Rectangle du bas
    cnv.setLineWidth(1)
    cnv.rect(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, fill = False)

    # Copyright
    cnv.setFont('Helvetica', 8)
    cnv.drawCentredString(midX, marginY - 10, 'Copyright © Société Mycologique de Strasbourg')


    cnv.save()

def generateFicheTheme(size, com):
    sizeX = size[0]
    sizeY = size[1]
    midX = size[0] / 2
    midY = size[1] / 2
    marginX = 20
    marginY = 20
    cnv = canvas.Canvas('test.pdf', pagesize = size, verbosity = 1) # 115 x 85 mm

    # Rectangle du haut
    cnv.setStrokeColorRGB((133 / 255), (133 / 255), (133 / 255))
    cnv.setLineWidth(2)
    cnv.setFillColorRGB((133 / 255), (133 / 255), (133 / 255))
    cnv.rect(0, sizeY - (2 * marginY), sizeX, 2 * marginY, fill = True)
    
    # Numero de fiche
    cnv.setStrokeColorRGB(0,0,0)
    cnv.setFillColorRGB(1,1,1)
    cnv.drawRightString(sizeX - marginX, sizeY - (marginY + 5), 'Fiche #2458')

    # Theme
    cnv.drawString(marginX, sizeY - (marginY + 5), 'Theme')
    cnv.setFillColorRGB(0,1,1)
    cnv.setFont('Helvetica', 14)
    cnv.drawCentredString(midX, sizeY - (marginY + 5), ' themevar') 

    # Genre et Espece
    cnv.setFillColorRGB(0,0,0)
    cnv.setFont('Helvetica', 14)
    cnv.drawString(marginX, sizeY - (3 * marginY), 'Foo Bar')

    # Variete et Forme
    cnv.setFont('Helvetica', 11)
    cnv.drawString(marginX, sizeY - (4 * marginY), 'Variété / Forme')


    # Noms usuels
    cnv.drawString(2 * marginX, midY + (0.5 * marginY), 'Noms usuels, ...')

    # Texte comestibilite
    if (com == 'C'):
        com_txt = 'Comestible'
        com_img = 'pdf_assets/Comest.bmp'
    elif (com == 'NC'):
        com_txt = 'Non Comestible'
        com_img = 'NonCom.bmp'
    elif (com == 'T'):
        com_txt = 'Toxique'
        com_img = 'Toxique.bmp'
    else:
        com_txt = 'Mortel'
        com_img = 'Mortel.bmp'

    img_width = 138.75 / 2.5
    img_height = 131.25 / 2.5
    
    cnv.drawImage(com_img, sizeX - marginX - img_width, midY + (0.5 * marginY), width = img_width, height= img_width)
    cnv.drawRightString(sizeX - marginX, midY - (0 * marginY) - 5, com_txt)

    # Observations
    cnv.setFont('Helvetica', 10)
    cnv.drawString(marginX + 10, (sizeX / 6) - 5, 'Blablablablablabla . . .')

    # Rectangle du bas
    cnv.setLineWidth(1)
    cnv.rect(0 + marginX, 5 + marginY, sizeX - (2 * marginX), sizeY / 6, fill = False)

    # Copyright
    cnv.setFont('Helvetica', 8)
    cnv.drawCentredString(midX, marginY - 10, 'Copyright © Société Mycologique de Strasbourg')


    cnv.save()

generateFicheTheme((325.984, 240.945), 'C')