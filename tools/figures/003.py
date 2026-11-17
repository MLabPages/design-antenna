from PIL import Image, ImageDraw, ImageFont
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(v*S)
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'
d.text((s(72),s(52)),'データインク比',font=F(bold,48),fill=INK)
tw=d.textlength('データインク比',font=F(bold,48))
d.text((s(72)+tw+s(22),s(70)),'Data-Ink Ratio — インクはデータのために',font=F(reg,26),fill=MUTE)
colw=(1600-72*2-56)/2
labels=['A','B','C','D','E']; vals=[42,58,35,71,49]
def panel(x0,good):
    col='#2E7D6B' if good else '#C8553D'
    cy=172; r=20; cx=x0+20
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=col)
    mk='○' if good else '×'; f=F(bold,24); mw=d.textlength(mk,font=f)
    d.text((s(cx)-mw/2,s(cy)),mk,font=f,fill='white',anchor='lm')
    lab='良い例' if good else '悪い例'
    d.text((s(x0+54),s(cy)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x0+54)+lw+s(14),s(cy)),'消して、数字を主役に' if good else '飾りの線が、データを埋もれさせる',font=F(reg,26),fill=SUB,anchor='lm')
    top,bot=210,770
    d.rounded_rectangle((s(x0)+s(2),s(top)+s(4),s(x0+colw)+s(2),s(bot)+s(4)),radius=s(14),fill='#E6E2D9')
    d.rounded_rectangle((s(x0),s(top),s(x0+colw),s(bot)),radius=s(14),fill='white')
    # plot area
    pl,pr,pt,pb = x0+100, x0+colw-50, top+70, bot-80
    vmax=80
    def Y(v): return pb-(pb-pt)*v/vmax
    n=len(vals); slot=(pr-pl)/n; bw=slot*0.56
    if not good:
        d.rectangle((s(pl),s(pt),s(pr),s(pb)),fill='#D9DCE1',outline='#22252B',width=s(4))
        for v in range(0,81,10):
            d.line((s(pl),s(Y(v)),s(pr),s(Y(v))),fill='#7E848D',width=s(2))
            d.text((s(pl-14),s(Y(v))),str(v),font=F(reg,20),fill=SUB,anchor='rm')
        for i in range(n+1):
            x=pl+slot*i; d.line((s(x),s(pt),s(x),s(pb)),fill='#7E848D',width=s(2))
        pal=['#C8553D','#E0A33A','#3D7CC8','#7A4FB3','#3FA06B']
        for i,v in enumerate(vals):
            xa=pl+slot*i+(slot-bw)/2
            d.rectangle((s(xa+10),s(Y(v)-10),s(xa+bw+10),s(pb)),fill='#8A8F97')  # fake shadow
            d.rectangle((s(xa),s(Y(v)),s(xa+bw),s(pb)),fill=pal[i],outline='#22252B',width=s(3))
            for k in range(int(Y(v))+8,int(pb),16):
                d.line((s(xa+4),s(k),s(xa+bw-4),s(k)),fill='#FFFFFF',width=s(2))
            d.text((s(xa+bw/2),s(pb+24)),labels[i],font=F(bold,26),fill=INK,anchor='mm')
        # legend box
        lx,ly=pl+16,pt+14
        d.rectangle((s(lx),s(ly),s(lx+150),s(ly+5*28+16)),fill='white',outline='#22252B',width=s(2))
        for i in range(5):
            yy=ly+14+i*28
            d.rectangle((s(lx+12),s(yy),s(lx+32),s(yy+18)),fill=pal[i])
            d.text((s(lx+44),s(yy+9)),'条件'+labels[i],font=F(reg,18),fill=INK,anchor='lm')
    else:
        d.line((s(pl-10),s(pb),s(pr+10),s(pb)),fill='#9AA0A8',width=s(2))
        for i,v in enumerate(vals):
            xa=pl+slot*i+(slot-bw)/2
            c='#2E5E8C' if v==max(vals) else '#B9C3CE'
            d.rectangle((s(xa),s(Y(v)),s(xa+bw),s(pb)),fill=c)
            d.text((s(xa+bw/2),s(Y(v)-22)),str(v),font=F(bold,28),fill=INK if v==max(vals) else SUB,anchor='mm')
            d.text((s(xa+bw/2),s(pb+24)),'条件'+labels[i],font=F(reg,22),fill=SUB,anchor='mm')
x1=72; x2=72+colw+56
panel(x1,False); panel(x2,True)
d.text((s(800),s(830)),'背景・枠・格子・影・凡例を消し、値を直接書く。強調は1本だけ（数値は例です）',font=F(reg,26),fill=SUB,anchor='mm')
img.save(str(__import__('pathlib').Path(__file__).resolve().parents[2].joinpath('images','003.png')),optimize=True)
print(img.size)
