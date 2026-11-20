# デザインアンテナ第6回 図: 色覚の多様性に配慮した配色（Okabe–Ito パレット）
# 色覚シミュレーションは Machado, Oliveira & Fernandes (2009) の severity 1.0 行列を線形sRGBに適用
from PIL import Image, ImageDraw, ImageFont
import numpy as np, math
S=1.5
W,H=int(1600*S),int(1160*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'; INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img)

# --- Machado 2009 (severity 1.0) ---
PROT=np.array([[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]])
DEUT=np.array([[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]])
def to_lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def to_srgb(l):
    l=np.clip(l,0,1); c=np.where(l<=0.0031308,l*12.92,1.055*l**(1/2.4)-0.055); return (c*255+0.5).astype(np.uint8)
def simulate(im,M):
    a=np.asarray(im).astype(np.float64); lin=to_lin(a)
    out=lin@M.T; return Image.fromarray(to_srgb(out))

# --- chart drawing ---
PW,PH=460,300
xs=[0,1,2,3,4,5]
DATA=[[22,34,46,56,63,67],[18,27,36,43,49,54],[15,19,25,30,34,38]]  # 架空のデータ
def dashed(dr,pts,fill,width,dash,gap):
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        L=math.hypot(x2-x1,y2-y1); t=0
        while t<L:
            t2=min(t+dash,L)
            dr.line((x1+(x2-x1)*t/L,y1+(y2-y1)*t/L,x1+(x2-x1)*t2/L,y1+(y2-y1)*t2/L),fill=fill,width=width)
            t=t2+gap
def chart(cols,good):
    im=Image.new('RGB',(s(PW),s(PH)),'white'); dr=ImageDraw.Draw(im)
    x0,x1=s(56),s(PW-(120 if good else 30)); y0,y1=s(28),s(PH-46)
    def X(v): return x0+(x1-x0)*v/5
    def Y(v): return y1-(y1-y0)*(v-10)/60
    for g in (10,30,50,70):
        dr.line((x0,Y(g),x1,Y(g)),fill='#ECE9E3',width=s(1))
        dr.text((x0-s(10),Y(g)),str(g),font=F(reg,17),fill=MUTE,anchor='rm')
    dr.line((x0,y1,x1,y1),fill=SUB,width=s(2))
    for v in xs: dr.text((X(v),y1+s(8)),str(v),font=F(reg,17),fill=MUTE,anchor='mt')
    dr.text(((x0+x1)/2,y1+s(28)),'週',font=F(reg,16),fill=MUTE,anchor='mt')
    names=['条件A','条件B','条件C']
    for i,(ys,c) in enumerate(zip(DATA,cols)):
        pts=[(X(v),Y(y)) for v,y in zip(xs,ys)]
        if good:
            w=s(5)
            if i==0: dr.line(pts,fill=c,width=w,joint='curve')
            elif i==1: dashed(dr,pts,c,w,s(16),s(9))
            else: dashed(dr,pts,c,w,s(5),s(7))
            for (px,py) in pts:
                r=s(7)
                if i==0: dr.ellipse((px-r,py-r,px+r,py+r),fill=c,outline='white',width=s(2))
                elif i==1: dr.rectangle((px-r,py-r,px+r,py+r),fill=c,outline='white',width=s(2))
                else: dr.polygon([(px,py-r-s(2)),(px+r+s(1),py+r),(px-r-s(1),py+r)],fill=c,outline='white')
            dr.text((pts[-1][0]+s(16),pts[-1][1]),names[i],font=F(bold,24),fill=c,anchor='lm')
        else:
            dr.line(pts,fill=c,width=s(3),joint='curve')
    if not good:
        lx,ly=x0+s(14),y0+s(2)
        dr.rectangle((lx,ly,lx+s(122),ly+s(88)),fill='white',outline='#CFCAC0',width=s(1))
        for i,c in enumerate(cols):
            yy=ly+s(16)+i*s(27)
            dr.line((lx+s(10),yy,lx+s(36),yy),fill=c,width=s(3))
            dr.text((lx+s(44),yy),names[i],font=F(reg,17),fill=SUB,anchor='lm')
    return im

BADC=[(228,40,36),(54,168,64),(232,150,20)]          # 赤・緑・橙（よくある配色）
OI={'Vermilion':(213,94,0),'Blue':(0,114,178),'Orange':(230,159,0),'Sky Blue':(86,180,233),
    'bluish Green':(0,158,115),'Yellow':(240,228,66),'reddish Purple':(204,121,167),'Black':(0,0,0)}
GOODC=[OI['Vermilion'],OI['Blue'],OI['bluish Green']]

# header
t='色覚の多様性に配慮した配色'
d.text((s(72),s(48)),t,font=F(bold,46),fill=INK)
tw=d.textlength(t,font=F(bold,46))
d.text((s(72)+tw+s(22),s(66)),'Color Universal Design — Okabe–Ito パレット',font=F(reg,26),fill=MUTE)

def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')

TITLES=['一般的な色覚','P型（1型）シミュレーション','D型（2型）シミュレーション']
GAP=38
def row(y,cols,good):
    base=chart(cols,good)
    ims=[base,simulate(base,PROT),simulate(base,DEUT)]
    for k,im in enumerate(ims):
        x=72+k*(PW+GAP)
        d.text((s(x),s(y)),TITLES[k],font=F(bold if k==0 else reg,22),fill=INK if k==0 else SUB)
        d.rounded_rectangle((s(x)-s(1)+s(3),s(y+40)+s(4),s(x+PW)+s(3),s(y+40+PH)+s(4)),radius=s(8),fill='#E3DED4')
        img.paste(im,(s(x),s(y+40)))
        d.rectangle((s(x),s(y+40),s(x+PW),s(y+40+PH)),outline=LINE,width=s(2))
badge(92,160,False,'悪い例','赤・緑・橙を色だけで区別し、凡例で対応づける')
row(196,BADC,False)
badge(92,592,True,'良い例','Okabe–Ito の色＋線種・マーカー＋直接ラベル')
row(628,GOODC,True)
d.text((s(1528),s(978)),'グラフは架空のデータ／シミュレーションは Machado ら（2009）の2色覚モデル',font=F(reg,17),fill=MUTE,anchor='rm')

# palette band
yb=1000
d.rounded_rectangle((s(72),s(yb),s(1528),s(yb+130)),radius=s(14),fill='white')
d.text((s(104),s(yb+30)),'Okabe–Ito',font=F(bold,26),fill=INK)
d.text((s(104),s(yb+72)),'の8色',font=F(bold,26),fill=INK)
order=['Black','Orange','Sky Blue','bluish Green','Yellow','Blue','Vermilion','reddish Purple']
sx=270; step=157
for i,n in enumerate(order):
    r,g,b=OI[n]; x=sx+i*step
    d.rounded_rectangle((s(x),s(yb+22),s(x+130),s(yb+70)),radius=s(8),fill=(r,g,b),outline='#00000022' if False else None)
    d.text((s(x+65),s(yb+82)),f'#{r:02X}{g:02X}{b:02X}',font=F(bold,19),fill=INK,anchor='mt')
img.save('images/006.png')
print(img.size)

