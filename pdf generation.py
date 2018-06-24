#!/usr/bin/env python3
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
#width,height,msg,border,align,background
pdf.image('Flo.png',20,20,33)
pdf.multi_cell(0,10,'A secret has been encrypted and posted on the blockchain of the FLO cryptocurrency.',0,'C',False)
pdf.multi_cell(0,10,'The key to decrypt this secret has been split in 3 shares like this one. By design, the secret can be decrypted with any 2 of these shares.',0,'C',False)
pdf.multi_cell(0,10,'Bellow is the part of the key that belongs to this share',0,'C',False)
#add shared key using multi_cell
pdf.output('sharedkey.pdf','F')
