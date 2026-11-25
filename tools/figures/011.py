from PIL import Image, ImageDraw, ImageFont
import math
S=1.5
BW,BH=1600,1140
W,H=int(BW*S),int(BH*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'; INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; GHOST='#D5D8DD'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
# example data (fictional): 6 conditions x 10 time points, range 0-100
N=10
def ser(fn): return [fn(i/(N-1)) for i in range(N)]
data=[('A',ser(lambda t:20+60*t)),
      ('B',ser(lambda t:78-50*t)),
      ('C',ser(lambda t:48+4*math.sin(t*6))),
      ('D',ser(lambda t:25+55*math.exp(-((t-0.45)/0.2)**2))),
      ('E',ser(lambda t:70-40*math.exp(-((t-0.5)/0.22)**2))),
      ('F',ser(lambda t:30+50*max(0,t-0.6)/0.4))]
# Okabe-Ito colors for the bad chart
OI=['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00']
d.text((s(72),s(44)),'スモールマルチプル',font=F(bold,50),fill=INK)
tw=d.textlength('スモールマルチプル',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Small Multiples ─ 同じ形の小さなグラフを並べて比べる',font=F(reg,26),fill=MUTE)
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')
PY=200; PH=520; PW=690
def card(x):
    d.rounded_rectangle((s(x)+s(3),s(PY)+s(5),s(x+PW)+s(3),s(PY+PH)+s(5)),radius=s(12),fill='#E3DED4')
    d.rounded_rectangle((s(x),s(PY),s(x+PW),s(PY+PH)),radius=s(12),fill='white',outline=LINE,width=s(2))
def pts(vals,x0,y0,w,h):
    return [(s(x0+w*i/(N-1)),s(y0+h-h*v/100)) for i,v in enumerate(vals)]
# ---- BAD: spaghetti
bx=72
badge(bx+20,PY-46,False,'悪い例','6本を1枚に重ねる')
card(bx)
x0,y0,w,h=bx+70,PY+50,440,400
for k in range(0,101,25):
    yy=y0+h-h*k/100
    d.line((s(x0),s(yy),s(x0+w),s(yy)),fill='#EEF0F2',width=s(1))
    d.text((s(x0-14),s(yy)),str(k),font=F(reg,18),fill=MUTE,anchor='rm')
d.line((s(x0),s(y0+h),s(x0+w),s(y0+h)),fill=SUB,width=s(2))
for (lab,v),c in zip(data,OI):
    d.line(pts(v,x0,y0,w,h),fill=c,width=s(4),joint='curve')
# legend far away
lx,ly=bx+545,PY+70
d.text((s(lx),s(ly-6)),'凡例',font=F(bold,20),fill=SUB)
for k,((lab,v),c) in enumerate(zip(data,OI)):
    yy=ly+40+k*38
    d.line((s(lx),s(yy),s(lx+34),s(yy)),fill=c,width=s(5))
    d.text((s(lx+46),s(yy)),'条件'+lab,font=F(reg,20),fill=INK,anchor='lm')
d.text((s(bx+40),s(PY+PH-38)),'色と凡例を往復しないと、どれがどれかわからない',font=F(reg,21),fill=BAD,anchor='lm')
# ---- GOOD: small multiples 3x2, shared axes, ghost context
gx=838
badge(gx+20,PY-46,True,'良い例','同じ軸の小さなグラフを並べる')
card(gx)
cols,rows=3,2
mx0,my0=gx+46,PY+40
cw,ch=196,196; gapx,gapy=14,34
for idx,(lab,v) in enumerate(data):
    r_,c_=divmod(idx,cols)
    px=mx0+c_*(cw+gapx); py=my0+r_*(ch+gapy)
    ix,iy,iw,ih=px+10,py+40,cw-20,ch-62
    d.rectangle((s(px),s(py),s(px+cw),s(py+ch)),fill='#FAF9F6')
    d.text((s(px+10),s(py+20)),'条件'+lab,font=F(bold,22),fill=INK,anchor='lm')
    for k in (0,50,100):
        yy=iy+ih-ih*k/100
        d.line((s(ix),s(yy),s(ix+iw),s(yy)),fill='#ECEEF0',width=s(1))
    for (l2,v2) in data:
        if l2!=lab: d.line(pts(v2,ix,iy,iw,ih),fill=GHOST,width=s(2),joint='curve')
    d.line((s(ix),s(iy+ih),s(ix+iw),s(iy+ih)),fill=SUB,width=s(2))
    d.line(pts(v,ix,iy,iw,ih),fill=GOOD,width=s(5),joint='curve')
    e=pts(v,ix,iy,iw,ih)[-1]
    d.ellipse((e[0]-s(5),e[1]-s(5),e[0]+s(5),e[1]+s(5)),fill=GOOD)
d.text((s(gx+40),s(PY+PH-38)),'縦軸は全パネル共通（0〜100）。灰色の線はほかの条件',font=F(reg,21),fill=GOOD,anchor='lm')
# ---- axis rule strip
by=PY+PH+70
hd='並べるときの約束：軸の範囲をそろえる'
d.text((s(72),s(by)),hd,font=F(bold,26),fill=SUB,anchor='lm')
d.line((s(72)+d.textlength(hd,font=F(bold,26))+s(16),s(by),s(1528),s(by)),fill=LINE,width=s(2))
def mini(x,y,good,maxes,title,note):
    ww,hh=690,212
    d.rounded_rectangle((s(x),s(y),s(x+ww),s(y+hh)),radius=s(12),fill='white',outline=LINE,width=s(2))
    col=GOOD if good else BAD
    d.text((s(x+28),s(y+32)),('○ ' if good else '× ')+title,font=F(bold,24),fill=col,anchor='lm')
    vals=[90,30]
    for k,(val,mxv,lab) in enumerate(zip(vals,maxes,['条件A','条件B'])):
        px=x+40+k*200; py=y+64; pw,ph=160,100
        d.line((s(px),s(py+ph),s(px+pw),s(py+ph)),fill=SUB,width=s(2))
        d.line((s(px),s(py),s(px),s(py+ph)),fill=SUB,width=s(2))
        d.text((s(px-8),s(py)),str(mxv),font=F(reg,16),fill=MUTE,anchor='rm')
        d.text((s(px-8),s(py+ph)),'0',font=F(reg,16),fill=MUTE,anchor='rm')
        bh=ph*val/mxv
        d.rectangle((s(px+50),s(py+ph-bh),s(px+110),s(py+ph)),fill=col)
        d.text((s(px+80),s(py+ph+16)),lab+'  '+str(val),font=F(reg,17),fill=INK,anchor='mm')
    d.text((s(x+450),s(y+106)),note[0],font=F(bold,22),fill=INK,anchor='lm')
    d.text((s(x+450),s(y+140)),note[1],font=F(reg,20),fill=SUB,anchor='lm')
mini(72,by+30,False,[100,35],'軸がばらばら',('90と30が','同じ高さに見える'))
mini(838,by+30,True,[100,100],'軸をそろえる',('差が','そのまま見える'))
d.line((s(72),s(1062),s(1528),s(1062)),fill=LINE,width=s(2))
d.text((s(800),s(1100)),'「何と比べて？」に、並べた形で答える。',font=F(bold,30),fill=INK,anchor='mm')
d.text((s(1528),s(1128)),'図の数値は説明用の架空データ',font=F(reg,16),fill=MUTE,anchor='rm')
img=img.resize((BW,BH),Image.LANCZOS)
img.save('images/011.png',optimize=True)
