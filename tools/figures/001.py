from PIL import Image, ImageDraw, ImageFont
import glob
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bolds=glob.glob('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
bold=bolds[0] if bolds else reg
JP=0  # index 0 = JP in ttc
def F(path,size): return ImageFont.truetype(path,int(size*S),index=JP)
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
def s(v): return int(v*S)
INK='#1F2430'; SUB='#4A4F59'; MUTE='#6B6F78'; BAR='#C9CDD4'
# title
d.text((s(72),s(52)),'近接の法則',font=F(bold,48),fill=INK)
tw=d.textlength('近接の法則',font=F(bold,48))
d.text((s(72)+tw+s(22),s(70)),'Law of Proximity — 近いものは、ひとまとまりに見える',font=F(reg,26),fill=MUTE)
colw=(1600-72*2-56)/2
def panel(x0,good):
    col='#2E7D6B' if good else '#C8553D'
    y=150
    cx,cy,r=x0+20,y+22,20
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=col)
    mk='○' if good else '×'
    f=F(bold,24); mw=d.textlength(mk,font=f)
    d.text((s(cx)-mw/2,s(cy)),mk,font=f,fill='white',anchor='lm')
    lab='良い例' if good else '悪い例'
    d.text((s(x0+54),s(cy)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x0+54)+lw+s(14),s(cy)),'関係の強さで余白を変える' if good else 'すき間がどこも同じ',font=F(reg,26),fill=SUB,anchor='lm')
    # slide card
    top,bot=210,780
    d.rounded_rectangle((s(x0)+s(2),s(top)+s(4),s(x0+colw)+s(2),s(bot)+s(4)),radius=s(14),fill='#E6E2D9')
    d.rounded_rectangle((s(x0),s(top),s(x0+colw),s(bot)),radius=s(14),fill='white')
    px=x0+52; y=top+50
    widths=[(0.92,0.70),(0.88,0.60),(0.84,0.66)]
    fh=F(bold,32); barw=colw-104
    heads=['目的','方法','結果']
    for i,(h,(w1,w2)) in enumerate(zip(heads,widths)):
        d.text((s(px),s(y)),h,font=fh,fill=INK,anchor='lt'); y+=34
        y+= 14 if good else 32
        for j,w in enumerate((w1,w2)):
            d.rounded_rectangle((s(px),s(y),s(px+barw*w),s(y+14)),radius=s(7),fill=BAR); y+=14
            if j==0: y+= 14 if good else 32
        if i<2: y+= 64 if good else 32
    # brackets for good: show grouping subtly? keep clean.
    note='中は狭く、外は広く。枠も線も足していない' if good else '見出しが、上と下のどちらの説明か迷う'
    f=F(reg,25); nw=d.textlength(note,font=f)
    d.text((s(x0+colw/2)-nw/2,s(812)),note,font=f,fill=SUB)
panel(72,False); panel(72+colw+56,True)
img.save(str(__import__('pathlib').Path(__file__).resolve().parents[2].joinpath('images','001.png')),optimize=True)
print(bold, img.size)
