from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'; BLUE='#2F5D9E'; BAR='#C9CED6'
d.text((s(72),s(48)),'視覚的階層',font=F(bold,50),fill=INK)
tw=d.textlength('視覚的階層',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Visual Hierarchy — 見てほしい順に、強さの差をつける',font=F(reg,27),fill=MUTE)
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
def slide(x0,y0):
    d.rounded_rectangle((s(x0)+s(3),s(y0)+s(5),s(x0+SW)+s(3),s(y0+SH)+s(5)),radius=s(10),fill='#E3DED4')
    d.rounded_rectangle((s(x0),s(y0),s(x0+SW),s(y0+SH)),radius=s(10),fill='white',outline=LINE,width=s(2))
def bars(x0,y0,w,n,gap,col=BAR,h=11):
    for i in range(n):
        ww=w*(0.95 if i%2==0 else 0.7)
        d.rounded_rectangle((s(x0),s(y0+i*gap),s(x0+ww),s(y0+i*gap+h)),radius=s(5),fill=col)
def chart(x0,y0,w,h,col):
    vals=[0.35,0.55,0.95]; n=len(vals); bw=w/(n*2+1)
    for i,v in enumerate(vals):
        bx=x0+bw*(1+2*i); c=col if i==2 else BAR
        d.rectangle((s(bx),s(y0+h-(h-10)*v),s(bx+bw),s(y0+h)),fill=c)
    d.line((s(x0),s(y0+h),s(x0+w),s(y0+h)),fill=SUB,width=s(2))
PY=196
# BAD: everything same size, many accents
bx=72
badge(bx+20,PY-46,False,'悪い例','どれも同じ強さ')
slide(bx,PY)
f=F(reg,25)
rows=[('背景：先行研究と問い',INK),('方法：調査の対象と手順',INK),('結果：〇〇は△△を高めた',INK),('補足：限界と今後の課題',INK)]
for k,(t,c) in enumerate(rows):
    y=PY+40+k*62
    d.text((s(bx+44),s(y)),t,font=f,fill=c)
# competing highlights
d.rectangle((s(bx+44),s(PY+40+2*62+30),s(bx+44+d.textlength(rows[2][0],font=f)/S),s(PY+40+2*62+34)),fill=BAD)
d.text((s(bx+470),s(PY+40)),'重要！',font=F(bold,25),fill='#D9A400')
d.text((s(bx+470),s(PY+40+62)),'注目',font=F(bold,25),fill=BLUE)
d.text((s(bx+44),s(PY+290)),'出典：〇〇 (2026)',font=F(reg,22),fill=INK)
# GOOD: 3 levels
gx=838
badge(gx+20,PY-46,True,'良い例','大・中・小の3段階')
slide(gx,PY)
d.text((s(gx+44),s(PY+34)),'〇〇は△△を高めた',font=F(bold,46),fill=INK)
d.text((s(gx+44),s(PY+118)),'根拠：調査A・調査B',font=F(bold,26),fill=GOOD)
chart(gx+44,PY+166,300,110,GOOD)
bars(gx+390,PY+176,250,4,24)
d.text((s(gx+44),s(PY+292)),'出典：〇〇 (2026)',font=F(reg,18),fill=MUTE)
# squint test: blur each slide region
by=PY+SH+56
d.text((s(72),s(by-12)),'目を細めると（ぼかしテスト）',font=F(bold,26),fill=SUB,anchor='lm')
d.line((s(72)+d.textlength('目を細めると（ぼかしテスト）',font=F(bold,26))+s(16),s(by-12),s(1528),s(by-12)),fill=LINE,width=s(2))
TW,TH=345,165
for x0,good in ((bx,False),(gx,True)):
    crop=img.crop((s(x0),s(PY),s(x0+SW),s(PY+SH))).filter(ImageFilter.GaussianBlur(s(7))).resize((s(TW),s(TH)),Image.LANCZOS)
    m=Image.new('L',crop.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,crop.size[0]-1,crop.size[1]-1),radius=s(8),fill=255)
    img.paste(crop,(s(x0),s(by+16)),m)
    d.rounded_rectangle((s(x0),s(by+16),s(x0+TW),s(by+16+TH)),radius=s(8),outline=LINE,width=s(2))
    tx=x0+TW+28
    if good:
        d.text((s(tx),s(by+60)),'最初に見る場所が',font=F(bold,26),fill=GOOD)
        d.text((s(tx),s(by+98)),'ひとつに決まる',font=F(bold,26),fill=GOOD)
    else:
        d.text((s(tx),s(by+60)),'全部が同じ濃さ。',font=F(bold,26),fill=BAD)
        d.text((s(tx),s(by+98)),'どこから読むか迷う',font=F(bold,26),fill=BAD)
d.line((s(72),s(782),s(1528),s(782)),fill=LINE,width=s(2))
d.text((s(800),s(834)),'大きさ・色・余白で、いちばん大事なものを1つだけ強くします。',font=F(bold,30),fill=INK,anchor='mm')
img=img.resize((1600,900),Image.LANCZOS)
img.save('images/009.png',optimize=True)
