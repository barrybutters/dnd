"""Offline, paginated handouts and reference cards with embedded Bitstream Vera."""
import io, threading
from pathlib import Path
from reportlab import rl_config
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
_LOCK=threading.Lock()
_FONT=None

def font_name():
    global _FONT
    with _LOCK:
        if _FONT is None:
            import reportlab
            path=Path(reportlab.__file__).parent/'fonts'/'Vera.ttf'
            if path.exists():pdfmetrics.registerFont(TTFont('EmberVera',str(path)));_FONT='EmberVera'
            else:_FONT='Helvetica'
    return _FONT

def lines(text,font,size,width):
    output=[]
    for raw in text.replace('\r','').split('\n'):
        if not raw:output.append('');continue
        current=''
        for word in raw.split(' '):
            candidate=(current+' '+word).strip()
            if pdfmetrics.stringWidth(candidate,font,size)<=width:current=candidate;continue
            if current:output.append(current);current=''
            for char in word:
                if pdfmetrics.stringWidth(current+char,font,size)>width and current:output.append(current);current=''
                current+=char
        output.append(current)
    return output

def fit_title(text,font,width,size=18):
    text=text.replace('\n',' ')[:200]
    while pdfmetrics.stringWidth(text,font,size)>width and text:text=text[:-1]
    return text

def render_handout(title,text,layout='document'):
    if not isinstance(title,str) or not isinstance(text,str):raise ValueError('Handout title and text must be strings')
    if len(text)>200000 or len(title)>1000:raise ValueError('Handout text is too long')
    if not text.strip():raise ValueError('Add handout text first')
    title=title.strip() or 'Campaign handout';font=font_name();out=io.BytesIO();w,h=A4
    c=canvas.Canvas(out,pagesize=A4);c.setTitle(title);c.setAuthor('Ember Table');page=0
    def new_page():
        nonlocal page
        if page:c.showPage()
        page+=1;c.setFillColorRGB(.14,.23,.18);c.setFont(font,9);c.drawString(42,h-35,'EMBER TABLE  /  '+('REFERENCE CARDS' if layout=='cards' else 'CAMPAIGN HANDOUT'))
        c.setFillColorRGB(.15,.18,.14);c.setFont(font,18);c.drawString(42,h-66,fit_title(title,font,w-84));c.setStrokeColorRGB(.72,.67,.49);c.line(42,h-78,w-42,h-78)
        c.setFillColorRGB(.4,.43,.39);c.setFont(font,8);c.drawString(42,28,'Prepared locally - Ember Table');c.drawRightString(w-42,28,str(page))
    new_page()
    if layout=='cards':
        gap=14;cw=(w-84-gap)/2;ch=170;top=h-96;rows=int((h-145)//(ch+gap));per=rows*2;slot=0
        for block in text.split('\n\n'):
            body=lines(block,font,9,cw-24)
            if not body:continue
            max_lines=13
            for start in range(0,len(body),max_lines):
                if slot and slot%per==0:new_page()
                local=slot%per;col=local%2;row=local//2;x=42+col*(cw+gap);y=top-row*(ch+gap)-ch
                c.setFillColorRGB(.97,.96,.91);c.setStrokeColorRGB(.7,.69,.58);c.roundRect(x,y,cw,ch,7,fill=1,stroke=1);c.setFillColorRGB(.16,.22,.17);c.setFont(font,9)
                for i,line in enumerate(body[start:start+max_lines]):c.drawString(x+12,y+ch-19-i*11,line)
                slot+=1
    else:
        y=h-103;c.setFillColorRGB(.13,.16,.13);c.setFont(font,10)
        for line in lines(text,font,10,w-84):
            if y<55:new_page();y=h-103;c.setFillColorRGB(.13,.16,.13);c.setFont(font,10)
            c.drawString(42,y,line);y-=14
    c.save();return out.getvalue()
