"""Original vector-like D20, ember and quill emblem, rendered at multiple sizes."""
from PIL import Image, ImageDraw
from pathlib import Path
import math
scale=4
im=Image.new('RGBA',(256*scale,256*scale));d=ImageDraw.Draw(im)
def poly(points,fill,outline=None,width=1):d.polygon([(x*scale,y*scale) for x,y in points],fill=fill);d.line([(x*scale,y*scale) for x,y in points+[points[0]]],fill=outline or fill,width=width*scale,joint='curve')
d.rounded_rectangle((8*scale,8*scale,248*scale,248*scale),radius=48*scale,fill='#142e25',outline='#d4b475',width=5*scale)
pts=[(128,29),(211,80),(211,173),(128,224),(45,173),(45,80)]
poly(pts,'#284d3a','#d4b475',4)
for a,b in [((128,29),(87,102)),((128,29),(171,102)),((45,80),(87,102)),((211,80),(171,102)),((45,173),(87,102)),((211,173),(171,102)),((128,224),(87,102)),((128,224),(171,102)),((87,102),(171,102))]:d.line(tuple(v*scale for p in [a,b] for v in p),fill='#d4b475',width=3*scale)
poly([(128,76),(108,112),(114,137),(128,151),(146,137),(149,114),(137,122),(140,98)],'#f39948')
poly([(128,110),(120,132),(128,143),(137,132)],'#ffe8ad')
poly([(153,149),(187,110),(194,105),(190,120),(158,155),(142,170)],'#f1dfb1')
d.line((142*scale,170*scale,187*scale,117*scale),fill='#d4b475',width=3*scale)
root=Path(__file__).resolve().parents[1]/'app'
im.resize((256,256),Image.Resampling.LANCZOS).save(root/'ember-table.png')
im.save(root/'ember-table.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
