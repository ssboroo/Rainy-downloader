"""Reproducible R monogram, with antialiased sizes for Windows and browsers."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent

def generate():
    size=1024
    image=Image.new('RGBA',(size,size));pixels=image.load()
    for y in range(size):
        t=y/(size-1);color=tuple(round(a+(b-a)*t) for a,b in zip((58,136,255),(30,76,216)))+(255,)
        for x in range(size):pixels[x,y]=color
    mask=Image.new('L',(size,size));ImageDraw.Draw(mask).rounded_rectangle((0,0,size-1,size-1),radius=235,fill=255);image.putalpha(mask)
    # Geometric R outline: stem, rounded upper bowl and diagonal leg.
    glyph=Image.new('L',(size,size));d=ImageDraw.Draw(glyph)
    d.rounded_rectangle((278,215,423,817),radius=22,fill=255)
    d.rounded_rectangle((330,215,774,600),radius=170,fill=255)
    d.rounded_rectangle((421,345,629,474),radius=61,fill=0)
    d.polygon([(488,541),(636,530),(797,817),(627,817),(480,562)],fill=255)
    image.paste((255,255,255,255),(0,0,size,size),glyph)
    folder=ROOT/'extension/icons';folder.mkdir(parents=True,exist_ok=True)
    for n in [16,48,128,256,512]:image.resize((n,n),Image.Resampling.LANCZOS).save(folder/f'{n}.png')
    image.resize((256,256),Image.Resampling.LANCZOS).save(folder/'rainy.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
if __name__=='__main__':generate()
