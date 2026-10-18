"""Original synthetic mixed text/image manual; never embeds a supplied rulebook."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image,ImageDraw

def prepare(path):
 c=canvas.Canvas(str(path),pagesize=(600,800));c.setFillColorRGB(.12,.2,.16);c.rect(0,0,600,800,fill=1,stroke=0);c.setFillColorRGB(.93,.83,.6);c.setFont('Helvetica-Bold',25);c.drawString(45,730,'EMBER MARSH BEAST');c.setFont('Helvetica',16);c.drawString(45,680,'Armor Class 14');c.drawString(45,650,'Hit Points 31');c.drawString(45,605,'Original synthetic manual - page one.');c.showPage()
 im=Image.new('RGB',(600,800),'#e6d6ae');d=ImageDraw.Draw(im);d.rectangle((40,40,560,760),outline='#32543f',width=8);d.ellipse((160,180,440,460),fill='#496d4b');d.polygon([(180,210),(220,100),(270,215)],fill='#496d4b');d.ellipse((240,270,260,290),fill='#e4b762');d.text((70,600),'IMAGE-ONLY REFERENCE PAGE',fill='#163322');c.drawImage(ImageReader(im),0,0,width=600,height=800);c.save()
if __name__=='__main__':prepare(Path('tests/manual-fixture.pdf'))
