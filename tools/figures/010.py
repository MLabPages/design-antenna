from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=1.5
BW,BH=1600,940
W,H=int(BW*S),int(BH*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; BAR='#C9CED6'
d.text((s(72),s(44)),'Less, but better',font=F(bold,50),fill=INK)
tw=d.textlength('Less, but better',font=F(bold,50))
d.text((s(72)+tw+s(24),s(66)),'ディーター・ラムス「良いデザインの10原則」の10番目',font=F(reg,26),fill=MUTE)
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')
SW,SH=690,330
PY=196
def shadow(x0,y0):
    d.rounded_rectangle((s(x0)+s(3),s(y0)+s(5),s(x0+SW)+s(3),s(y0+SH)+s(5)),radius=s(10),fill='#E3DED4')
# ---- BAD slide: decoration on top of decoration
bx=72
badge(bx+20,PY-46,False,'悪い例','飾りが主役')
shadow(bx,PY)
g=Image.new('RGB',(s(SW),s(SH)))
gd=ImageDraw.Draw(g)
c1=(122,72,170); c2=(240,150,60)
for x in range(s(SW)):
    t=x/s(SW); gd.line((x,0,x,s(SH)),fill=tuple(int(a+(b-a)*t) for a,b in zip(c1,c2)))
m=Image.new('L',g.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,g.size[0]-1,g.size[1]-1),radius=s(10),fill=255)
img.paste(g,(s(bx),s(PY)),m)
d.rounded_rectangle((s(bx+12),s(PY+12),s(bx+SW-12),s(PY+SH-12)),radius=s(8),outline=(255,230,90),width=s(4))
d.rounded_rectangle((s(bx+20),s(PY+20),s(bx+SW-20),s(PY+SH-20)),radius=s(6),outline=(255,255,255,150),width=s(2))
# garish title: outline + shadow, mixed colors
tf=F(bold,38)
d.text((s(bx+48)+s(4),s(PY+40)+s(4)),'驚きの結果！！',font=tf,fill=(0,0,0,110))
d.text((s(bx+48),s(PY+40)),'驚きの結果！！',font=tf,fill=(255,236,80),stroke_width=s(2),stroke_fill=(190,30,60))
# stars
import math
def star(cx,cy,r,col):
    pts=[]
    for k in range(10):
        a=-math.pi/2+k*math.pi/5; rr=r if k%2==0 else r*0.45
        pts.append((s(cx+rr*math.cos(a)),s(cy+rr*math.sin(a))))
    d.polygon(pts,fill=col)
star(bx+560,PY+66,26,(255,236,80)); star(bx+612,PY+108,15,(255,255,255,220)); star(bx+520,PY+118,11,(255,180,200))
# 3D bars, every bar a different color
cols=[(80,200,255),(255,90,150),(120,240,120)]
vals=[0.4,0.6,0.95]
x0,y0,hh=bx+70,PY+130,150
for k,(v,c) in enumerate(zip(vals,cols)):
    xx=x0+k*110; top=y0+hh-(hh-10)*v; w=60; dp=16
    dark=tuple(int(a*0.65) for a in c); light=tuple(min(255,int(a*1.15)) for a in c)
    d.polygon([(s(xx+w),s(top)),(s(xx+w+dp),s(top-dp)),(s(xx+w+dp),s(y0+hh-dp)),(s(xx+w),s(y0+hh))],fill=dark)
    d.polygon([(s(xx),s(top)),(s(xx+dp),s(top-dp)),(s(xx+w+dp),s(top-dp)),(s(xx+w),s(top))],fill=light)
    d.rectangle((s(xx),s(top),s(xx+w),s(y0+hh)),fill=c)
d.line((s(x0-10),s(y0+hh),s(x0+340),s(y0+hh)),fill='white',width=s(3))
# clip-art circles / icon stamps
for (cx,cy,r,c) in ((bx+480,PY+215,34,(255,255,255,90)),(bx+560,PY+245,24,(80,200,255,200)),(bx+610,PY+200,18,(255,90,150,200))):
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=c,outline='white',width=s(3))
d.text((s(bx+455),s(PY+280)),'出典：〇〇 (2026)',font=F(reg,18),fill=(255,255,255,210))
# ---- GOOD slide
gx=838
badge(gx+20,PY-46,True,'良い例','伝えるものだけ')
shadow(gx,PY)
d.rounded_rectangle((s(gx),s(PY),s(gx+SW),s(PY+SH)),radius=s(10),fill='white',outline=LINE,width=s(2))
d.text((s(gx+48),s(PY+40)),'〇〇は△△を高めた',font=F(bold,40),fill=INK)
x0,y0,hh=gx+60,PY+130,150
for k,v in enumerate(vals):
    xx=x0+k*110; top=y0+hh-(hh-10)*v
    d.rectangle((s(xx),s(top),s(xx+60),s(y0+hh)),fill=GOOD if k==2 else BAR)
d.line((s(x0-12),s(y0+hh),s(x0+300),s(y0+hh)),fill=SUB,width=s(2))
d.text((s(gx+420),s(PY+180)),'条件Cで',font=F(bold,26),fill=GOOD)
d.text((s(gx+420),s(PY+218)),'最も高い',font=F(bold,26),fill=GOOD)
d.text((s(gx+48),s(PY+294)),'出典：〇〇 (2026)',font=F(reg,18),fill=MUTE)
# ---- the ten principles
by=PY+SH+64
hd='10の原則（Vitsœ 公式の英文を要約）'
d.text((s(72),s(by)),hd,font=F(bold,26),fill=SUB,anchor='lm')
d.line((s(72)+d.textlength(hd,font=F(bold,26))+s(16),s(by),s(1528),s(by)),fill=LINE,width=s(2))
labs=['革新的である','役に立つ','美しい','わかりやすい','控えめである','誠実である','長く使える','細部まで徹底','環境にやさしい','できるだけ少なく']
CW=(1456-4*16)/5; CH=74
for k,lab in enumerate(labs):
    r_,c_=divmod(k,5)
    x=72+c_*(CW+16); y=by+30+r_*(CH+14)
    hi=(k==9)
    d.rounded_rectangle((s(x),s(y),s(x+CW),s(y+CH)),radius=s(12),fill=INK if hi else 'white',outline=None if hi else LINE,width=s(2))
    cx,cy=x+38,y+CH/2
    d.ellipse((s(cx-20),s(cy-20),s(cx+20),s(cy+20)),fill=GOOD if hi else '#ECE8DF')
    d.text((s(cx),s(cy)),str(k+1),font=F(bold,22 if k<9 else 19),fill='white' if hi else SUB,anchor='mm')
    d.text((s(x+72),s(cy)),lab,font=F(bold if hi else reg,23 if hi else 25),fill='white' if hi else INK,anchor='lm')
d.line((s(72),s(842),s(1528),s(842)),fill=LINE,width=s(2))
d.text((s(800),s(890)),'足す前に問う：それは、伝えるのに必要か。',font=F(bold,32),fill=INK,anchor='mm')
img=img.resize((BW,BH),Image.LANCZOS)
img.save('images/010.png',optimize=True)
