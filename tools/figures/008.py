from PIL import Image, ImageDraw, ImageFont
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img,'RGBA')
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; BLUE='#2F5D9E'; BAR='#C9CED6'
d.text((s(72),s(48)),'グリッドシステム',font=F(bold,50),fill=INK)
tw=d.textlength('グリッドシステム',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Grid Systems — 見えない「列」に、そろえて置く',font=F(reg,27),fill=MUTE)
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')
SW,SH=690,388
def slide(x0,y0):
    d.rounded_rectangle((s(x0)+s(3),s(y0)+s(5),s(x0+SW)+s(3),s(y0+SH)+s(5)),radius=s(10),fill='#E3DED4')
    d.rounded_rectangle((s(x0),s(y0),s(x0+SW),s(y0+SH)),radius=s(10),fill='white',outline=LINE,width=s(2))
def chart(x0,y0,w,h):
    d.rectangle((s(x0),s(y0),s(x0+w),s(y0+h)),fill='#EEF2F8')
    vals=[0.45,0.7,0.55,0.9]; n=len(vals); bw=w/(n*2+1)
    for i,v in enumerate(vals):
        bx=x0+bw*(1+2*i); d.rectangle((s(bx),s(y0+h-14-(h-40)*v),s(bx+bw),s(y0+h-14)),fill=BLUE)
    d.line((s(x0+10),s(y0+h-14),s(x0+w-10),s(y0+h-14)),fill=SUB,width=s(2))
def bars(x0,y0,w,n,gap=30):
    for i in range(n):
        ww=w*(0.92 if i%3!=2 else 0.62)
        d.ellipse((s(x0),s(y0+i*gap+3),s(x0+9),s(y0+i*gap+12)),fill=SUB)
        d.rounded_rectangle((s(x0+20),s(y0+i*gap+2),s(x0+20+ww-20),s(y0+i*gap+13)),radius=s(5),fill=BAR)
def vdash(x,y0,y1,col,dash=8,gap=6,wd=2):
    y=y0
    while y<y1:
        d.line((s(x),s(y),s(x),s(min(y+dash,y1))),fill=col,width=s(wd)); y+=dash+gap
PY=230
# BAD
bx=72
badge(bx+20,PY-46,False,'悪い例','空いたところに、なんとなく置く')
slide(bx,PY)
d.text((s(bx+52),s(PY+34)),'研究タイトル',font=F(bold,32),fill=INK)
chart(bx+31,PY+108,330,200)
bars(bx+395,PY+122,240,4,34)
bars(bx+380,PY+268,200,2,30)
d.text((s(bx+66),s(PY+338)),'出典：〇〇 (2026)',font=F(reg,18),fill=MUTE)
for x in (bx+31,bx+52,bx+66):
    vdash(x,PY+20,PY+SH-14,BAD)
for x in (bx+380,bx+395):
    vdash(x,PY+100,PY+320,BAD)
# GOOD
gx=838
badge(gx+20,PY-46,True,'良い例','図は1〜7列、本文は8〜12列')
slide(gx,PY)
M,G=40,12; CWc=(SW-2*M-11*G)/12
def cx(i): return gx+M+i*(CWc+G)
for i in range(12):
    d.rectangle((s(cx(i)),s(PY+2),s(cx(i)+CWc),s(PY+SH-2)),fill=(200,85,61,26))
d.text((s(cx(0)),s(PY+34)),'研究タイトル',font=F(bold,32),fill=INK)
chart(cx(0),PY+108,cx(6)+CWc-cx(0),200)
bars(cx(7),PY+122,cx(11)+CWc-cx(7),4,34)
bars(cx(7),PY+268,cx(11)+CWc-cx(7),2,30)
d.text((s(cx(0)),s(PY+338)),'出典：〇〇 (2026)',font=F(reg,18),fill=MUTE)
vdash(cx(0),PY+20,PY+SH-14,GOOD,wd=3)
vdash(cx(7),PY+100,PY+320,GOOD,wd=3)
# anatomy labels under good slide
ay=PY+SH+26
def bracket(x0,x1,lab,col=SUB):
    d.line((s(x0),s(ay),s(x1),s(ay)),fill=col,width=s(2))
    for x in (x0,x1): d.line((s(x),s(ay-8),s(x),s(ay+2)),fill=col,width=s(2))
d.text((s(gx-4),s(ay+16)),'マージン',font=F(bold,24),fill=SUB)
bracket(gx,gx+M,'')
bracket(cx(3),cx(3)+CWc,'')
d.text((s(cx(3)+CWc/2),s(ay+16)),'列',font=F(bold,24),fill=SUB,anchor='ma')
bracket(cx(8)+CWc,cx(9),'')
d.text((s(cx(8)+CWc+G/2),s(ay+16)),'ガター',font=F(bold,24),fill=SUB,anchor='ma')
# bad caption
d.text((s(bx),s(ay+16)),'左端が5か所でばらばら → がたついて見える',font=F(reg,24),fill=BAD)
# bottom message
d.line((s(72),s(752),s(1528),s(752)),fill=LINE,width=s(2))
d.text((s(800),s(800)),'左端の線を2本にしぼるだけで、スライドは整って見えます。',font=F(bold,30),fill=INK,anchor='mm')
img=img.resize((1600,900),Image.LANCZOS)
img.save('images/008.png',optimize=True)

