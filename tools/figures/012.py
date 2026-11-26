from PIL import Image, ImageDraw, ImageFont
# 第12回 行間（Line Spacing） 図。PILで描画（日本語はベタ組で1字ずつ字面枠に配置）
S=1.5
BW,BH=1600,1120
W,H=int(BW*S),int(BH*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'; INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; ACC='#3A6EA5'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
d.text((s(72),s(44)),'行間',font=F(bold,50),fill=INK)
tw=d.textlength('行間',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Line Spacing ─ 行と行のあいだの「空き」で、読みやすさが決まる',font=F(reg,26),fill=MUTE)

def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(12),s(y+2)),sub,font=F(reg,22),fill=SUB,anchor='lm')

TEXT='行間は、行と行の空きです。狭いと次の行を見失い、広いと段落に見えません。'
PER=12; FS=34
# 行頭禁則（句読点が行頭に来ない）を守るため、改行位置は手で決める
lines=['行間とは、行と行の空き','のこと。狭いと次の行を','見失い、広いと段落に','見えなくなります。']
def para(x,y,gap,size=FS,color=INK,font=reg):
    f=F(font,size)
    for li,ln in enumerate(lines):
        top=y+li*(size+gap)
        for ci,ch in enumerate(ln):
            cx=x+ci*size+size/2; cy=top+size/2
            d.text((s(cx),s(cy)),ch,font=f,fill=color,anchor='mm')
    return y+len(lines)*(size+gap)-gap

PY=200; PH=430; PW=462; GAPC=27
cards=[(False,'詰めすぎ','行間 0.1字分',0.1,'次の行を見失いやすい'),
       (True,'ちょうどよい','行間 0.7字分',0.7,'行を目で追いやすい'),
       (False,'空けすぎ','行間 1.6字分',1.6,'ひとつの段落に見えない')]
for k,(good,lab,sub,g,note) in enumerate(cards):
    x=72+k*(PW+GAPC)
    badge(x+20,PY-46,good,lab,sub)
    d.rounded_rectangle((s(x)+s(3),s(PY)+s(5),s(x+PW)+s(3),s(PY+PH)+s(5)),radius=s(12),fill='#E3DED4')
    d.rounded_rectangle((s(x),s(PY),s(x+PW),s(PY+PH)),radius=s(12),fill='white',outline=(GOOD if good else LINE),width=s(3 if good else 2))
    tx=x+(PW-PER*FS)/2
    blockh=len(lines)*FS+(len(lines)-1)*FS*g
    ty=PY+24+(310-blockh)/2
    para(tx,ty,FS*g)
    d.line((s(x+28),s(PY+PH-70),s(x+PW-28),s(PY+PH-70)),fill='#EEF0F2',width=s(1))
    d.text((s(x+PW/2),s(PY+PH-36)),note,font=F(reg,24),fill=(GOOD if good else BAD),anchor='mm')

# ---- 下段：しくみ
BY=PY+PH+50
d.text((s(72),s(BY)),'しくみ：行送り ＝ 文字サイズ ＋ 行間',font=F(bold,32),fill=INK)
# anatomy (left)
AX=96; AY=BY+78; AS=78; AG=AS*0.7
words=['行を','追う']
for li,wd in enumerate(words):
    top=AY+li*(AS+AG)
    for ci,ch in enumerate(wd):
        x0=AX+ci*AS
        d.rectangle((s(x0),s(top),s(x0+AS),s(top+AS)),outline='#C9CED6',width=s(1))
        d.text((s(x0+AS/2),s(top+AS/2)),ch,font=F(reg,AS),fill=INK,anchor='mm')
# gap band
gx0=AX; gx1=AX+2*AS
d.rectangle((s(gx0),s(AY+AS),s(gx1),s(AY+AS+AG)),fill=(58,110,165,40))
# brackets
def vbr(x,y0,y1,col,label,lx):
    d.line((s(x),s(y0),s(x),s(y1)),fill=col,width=s(3))
    d.line((s(x-8),s(y0),s(x+8),s(y0)),fill=col,width=s(3))
    d.line((s(x-8),s(y1),s(x+8),s(y1)),fill=col,width=s(3))
    d.text((s(lx),s((y0+y1)/2)),label,font=F(bold,24),fill=col,anchor='lm')
bx=AX+2*AS+30
vbr(bx,AY,AY+AS,SUB,'文字サイズ',bx+18)
vbr(bx,AY+AS,AY+AS+AG,ACC,'行間',bx+18)
bx2=bx+170
vbr(bx2,AY,AY+AS+AG,INK,'行送り',bx2+18)

# guideline (right)
RX=640; RY=BY+70
d.rounded_rectangle((s(RX),s(RY),s(RX+888),s(RY+330)),radius=s(12),fill='white',outline=LINE,width=s(2))
d.text((s(RX+36),s(RY+48)),'日本語の本文の目安',font=F(bold,28),fill=INK,anchor='lm')
rows=[('行間','文字の半分〜1字分'),('line-height','1.5〜2.0'),('1行が35字を超える','1字分に近づける')]
for i,(a,b) in enumerate(rows):
    yy=RY+118+i*62
    d.ellipse((s(RX+40),s(yy-6),s(RX+52),s(yy+6)),fill=GOOD)
    d.text((s(RX+72),s(yy)),a,font=F(reg,26),fill=SUB,anchor='lm')
    d.text((s(RX+400),s(yy)),b,font=F(bold,30),fill=INK,anchor='lm')
d.text((s(RX+36),s(RY+300)),'出典：W3C『日本語組版処理の要件（JLREQ）』',font=F(reg,19),fill=MUTE,anchor='lm')

img=img.resize((BW,BH),Image.LANCZOS)
img.save('images/012.png',optimize=True)
