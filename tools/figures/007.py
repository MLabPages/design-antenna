from PIL import Image, ImageDraw, ImageFont
import math
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; BLUE='#2F5D9E'
# header
d.text((s(72),s(48)),'フィッツの法則',font=F(bold,50),fill=INK)
tw=d.textlength('フィッツの法則',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),"Fitts's Law — 遠くて小さい的ほど、押すのに時間がかかる",font=F(reg,27),fill=MUTE)
# formula band
fy=150
d.rounded_rectangle((s(72),s(fy),s(1528),s(fy+190)),radius=s(14),fill='white',outline=LINE,width=s(2))
def cursor(x,y,k=1.0):
    pts=[(0,0),(0,34),(9,26),(16,42),(23,39),(16,24),(28,24)]
    P=[(s(x+px*k),s(y+py*k)) for px,py in pts]
    d.polygon(P,fill=INK)
cy=fy+95
cursor(120,cy-20)
tx=560; tw_=60
d.rectangle((s(tx),s(cy-45),s(tx+tw_),s(cy+45)),fill=BLUE)
# D arrow
ay=cy+65
d.line((s(130),s(ay),s(tx+tw_/2),s(ay)),fill=SUB,width=s(2))
for x,dirn in ((130,1),(tx+tw_/2,-1)):
    d.polygon([(s(x),s(ay)),(s(x+12*dirn),s(ay-6)),(s(x+12*dirn),s(ay+6))],fill=SUB)
d.text((s((130+tx+tw_/2)/2),s(ay-6)),'D 距離',font=F(bold,24),fill=SUB,anchor='mb')
# W arrow
wy=cy-62
d.line((s(tx),s(wy),s(tx+tw_),s(wy)),fill=SUB,width=s(2))
d.text((s(tx+tw_/2),s(wy-6)),'W 幅',font=F(bold,24),fill=SUB,anchor='mb')
# formula text
fx=720
def logtxt(x,y,pre,post,f,fsub,col):
    d.text((s(x),s(y)),pre+'log',font=f,fill=col)
    w1=d.textlength(pre+'log',font=f)
    d.text((s(x)+w1+s(1),s(y)+int(f.size*0.55)),'2',font=fsub,fill=col)
    w2=d.textlength('2',font=fsub)
    d.text((s(x)+w1+w2+s(4),s(y)),post,font=f,fill=col)
logtxt(fx,fy+40,'かかる時間  MT = a + b · ','( D / W + 1 )',F(bold,34),F(bold,20),INK)
d.text((s(fx),s(fy+100)),'近づける（D を小さく）か、大きくする（W を大きく）と速く、',font=F(reg,24),fill=SUB)
d.text((s(fx),s(fy+136)),'押しまちがいも減ります。a・b は人と機器で決まる定数。',font=F(reg,24),fill=SUB)
# panels
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')
def card(x0,y0,w,h):
    d.rounded_rectangle((s(x0)+s(3),s(y0)+s(5),s(x0+w)+s(3),s(y0+h)+s(5)),radius=s(12),fill='#E3DED4')
    d.rounded_rectangle((s(x0),s(y0),s(x0+w),s(y0+h)),radius=s(12),fill='white',outline=LINE,width=s(2))
def dashed_rect(x0,y0,x1,y1,col,dash=6,gap=5,wd=2):
    for (a,b,c,e) in ((x0,y0,x1,y0),(x0,y1,x1,y1),(x0,y0,x0,y1),(x1,y0,x1,y1)):
        L=math.hypot(c-a,e-b); n=0.0
        while n<L:
            m=min(n+dash,L)
            d.line((s(a+(c-a)*n/L),s(b+(e-b)*n/L),s(a+(c-a)*m/L),s(b+(e-b)*m/L)),fill=col,width=s(wd))
            n+=dash+gap
CW,CH=690,330
py0=430
# BAD
bx=72
badge(bx+20,py0-40,False,'悪い例','小さな文字リンクが詰まっている')
card(bx,py0,CW,CH)
d.text((s(bx+36),s(py0+32)),'論文タイトル（例）',font=F(bold,30),fill=INK)
d.text((s(bx+36),s(py0+80)),'著者名 ・ 学会誌名 ・ 2026',font=F(reg,22),fill=MUTE)
lx=bx+36; ly=py0+130
fs=F(reg,20)
for t in ['PDF','スライド','コード']:
    lw=d.textlength(t,font=fs)/S
    d.text((s(lx),s(ly)),t,font=fs,fill=BLUE)
    dashed_rect(lx-2,ly-1,lx+lw+2,ly+27,BAD,4,3,2)
    lx+=lw+14
d.text((s(bx+36),s(py0+190)),'押せる範囲は 高さ約28px、隣とのすき間は約10px。',font=F(reg,22),fill=SUB)
d.text((s(bx+36),s(py0+226)),'スマホでは隣のリンクを押してしまいがち。',font=F(reg,22),fill=SUB)
logtxt(bx+36,py0+CH-50,'難しさ ID = ','(600/28 + 1) ≈ 4.5 bit',F(bold,24),F(bold,15),BAD)
# GOOD
gx=838
badge(gx+20,py0-40,True,'良い例','大きなボタンを、間をあけて並べる')
card(gx,py0,CW,CH)
d.text((s(gx+36),s(py0+32)),'論文タイトル（例）',font=F(bold,30),fill=INK)
d.text((s(gx+36),s(py0+80)),'著者名 ・ 学会誌名 ・ 2026',font=F(reg,22),fill=MUTE)
bx2=gx+36; by2=py0+126; bh=56
fb=F(bold,24)
for t in ['PDF','スライド','コード']:
    lw=d.textlength(t,font=fb)/S
    bw=max(120,lw+56)
    d.rounded_rectangle((s(bx2),s(by2),s(bx2+bw),s(by2+bh)),radius=s(10),fill='#E8EEF7',outline=BLUE,width=s(2))
    d.text((s(bx2+bw/2),s(by2+bh/2)),t,font=fb,fill=BLUE,anchor='mm')
    bx2+=bw+20
d.text((s(gx+36),s(py0+206)),'高さ56px（44px以上）、すき間20px。',font=F(reg,22),fill=SUB)
d.text((s(gx+36),s(py0+242)),'指でもマウスでも、迷わず一度で押せる。',font=F(reg,22),fill=SUB)
logtxt(gx+36,py0+CH-50,'難しさ ID = ','(600/56 + 1) ≈ 3.6 bit',F(bold,24),F(bold,15),GOOD)
# footer
fy2=py0+CH+44
d.text((s(72),s(fy2)),'IDは、カーソルから600px先の的を押す場合。幅が2倍になると、難しさは約1bit下がります。',font=F(reg,22),fill=SUB)
d.text((s(72),s(fy2+40)),'目安：WCAG 2.2 では押せる範囲を 24×24 CSS px 以上（AA）、44×44 CSS px 以上（AAA）。',font=F(reg,22),fill=SUB)
img.save('/workspace/design-antenna/images/007.png')
print(math.log2(600/28+1), math.log2(600/56+1))
