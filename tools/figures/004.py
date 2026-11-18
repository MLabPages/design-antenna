from PIL import Image, ImageDraw, ImageFont
S=1.5
W,H=int(1600*S),int(1020*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(v*S)
FS=22
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'
TEXT=('1行が長すぎると、行末から次の行頭へ目を戻すときに、どの行を読んでいたのか見失いやすくなります。'
      '反対に短すぎると、目が何度も往復して読むリズムが途切れます。'
      '読みやすい長さには目安があり、欧文では1行45〜75字、和文では全角40字以内がひとつの基準です。'
      '研究サイトの本文やスライドの説明文も、段落の幅を決めてから文字の大きさを選ぶと、ぐっと読みやすくなります。')
NOHEAD='、。」）・'
def wrap(t,n):
    f=F(reg,FS); lim=s(n*FS)+1
    lines=[];cur=''
    for ch in t:
        if d.textlength(cur+ch,font=f)>lim and ch not in NOHEAD:
            lines.append(cur);cur=''
        cur+=ch
    if cur: lines.append(cur)
    return lines
d.text((s(72),s(50)),'行の長さ',font=F(bold,48),fill=INK)
tw=d.textlength('行の長さ',font=F(bold,48))
d.text((s(72)+tw+s(22),s(68)),'Line Length / Measure — 1行は短めに、行間はゆったり',font=F(reg,26),fill=MUTE)
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,26),fill=SUB,anchor='lm')
def card(x0,y0,x1,y1):
    d.rounded_rectangle((s(x0)+s(2),s(y0)+s(4),s(x1)+s(2),s(y1)+s(4)),radius=s(14),fill='#E6E2D9')
    d.rounded_rectangle((s(x0),s(y0),s(x1),s(y1)),radius=s(14),fill='white')
def bracket(x0,x1,y,col,label):
    d.line((s(x0),s(y),s(x1),s(y)),fill=col,width=s(3))
    d.line((s(x0),s(y-10),s(x0),s(y+10)),fill=col,width=s(3))
    d.line((s(x1),s(y-10),s(x1),s(y+10)),fill=col,width=s(3))
    f=F(bold,24); lw=d.textlength(label,font=f); mx=s((x0+x1)/2)
    d.rectangle((mx-lw/2-s(12),s(y-18),mx+lw/2+s(12),s(y+18)),fill='white')
    d.text((mx,s(y)),label,font=f,fill=col,anchor='mm')
# BAD
badge(92,170,False,'悪い例','1行が長く、行間も狭い → 次の行を見失う')
N1=60; lines=wrap(TEXT,N1); x0=72; y0=205
pad=40; tx=x0+pad
card(x0,y0,1528,y0+80+len(lines)*int(FS*1.2)+40)
bracket(tx,tx+N1*FS,y0+36,BAD,f'1行 約{N1}字')
fy=y0+70
for i,l in enumerate(lines):
    d.text((s(tx),s(fy+i*FS*1.2)),l,font=F(reg,FS),fill=INK)
# GOOD
gy=y0+80+len(lines)*int(FS*1.3)+40+70
badge(92,gy,True,'良い例','1行を短くし、行間を広げる → 目の戻りが楽')
N2=32; lines2=wrap(TEXT,N2); y1=gy+35
cw=N2*FS+pad*2
card(x0,y1,x0+cw,y1+80+len(lines2)*int(FS*1.8)+30)
bracket(tx,tx+N2*FS,y1+36,GOOD,f'1行 約{N2}字')
for i,l in enumerate(lines2):
    d.text((s(tx),s(y1+70+i*FS*1.8)),l,font=F(reg,FS),fill=INK)
# side note
nx=x0+cw+70; ny=y1+20
d.text((s(nx),s(ny)),'目安',font=F(bold,34),fill=INK)
items=[('欧文','45〜75字','（理想は66字・Bringhurst）'),('和文','40字以内','（WCAG 2.2 SC 1.4.8）'),('行間','文字の1.5倍以上','（同上）')]
for k,(a,b,c) in enumerate(items):
    yy=ny+80+k*120
    d.rounded_rectangle((s(nx),s(yy),s(nx+96),s(yy+52)),radius=s(10),fill='#E9F1EE')
    d.text((s(nx+48),s(yy+26)),a,font=F(bold,26),fill=GOOD,anchor='mm')
    d.text((s(nx+120),s(yy+26)),b,font=F(bold,38),fill=INK,anchor='lm')
    if c: d.text((s(nx+120),s(yy+70)),c,font=F(reg,22),fill=MUTE,anchor='lm')
d.text((s(72),s(980)),'出典：Bringhurst『The Elements of Typographic Style』／W3C WCAG 2.2 SC 1.4.8',font=F(reg,20),fill=MUTE)
img.save(str(__import__('pathlib').Path(__file__).resolve().parents[2].joinpath('images','004.png')))
print(gy, y1+80+len(lines2)*int(FS*1.8)+30)
