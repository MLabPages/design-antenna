from PIL import Image, ImageDraw, ImageFont
S=1.5
W,H=int(1600*S),int(980*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'
# header
d.text((s(72),s(52)),'アサーション・エビデンス',font=F(bold,48),fill=INK)
tw=d.textlength('アサーション・エビデンス',font=F(bold,48))
d.text((s(72)+tw+s(22),s(70)),'Assertion–Evidence — 見出しは「主張の文」、本文は「証拠の図」',font=F(reg,26),fill=MUTE)
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(14),s(y)),sub,font=F(reg,24),fill=SUB,anchor='lm')
def slide(x0,y0,w,h):
    d.rounded_rectangle((s(x0)+s(3),s(y0)+s(5),s(x0+w)+s(3),s(y0+h)+s(5)),radius=s(10),fill='#E3DED4')
    d.rounded_rectangle((s(x0),s(y0),s(x0+w),s(y0+h)),radius=s(10),fill='white',outline=LINE,width=s(2))
SW,SH=700,394
# BAD slide
bx,by=72,200
badge(bx+20,160,False,'悪い例','見出しは単語、本文は箇条書き')
slide(bx,by,SW,SH)
d.text((s(bx+40),s(by+34)),'実験結果',font=F(bold,34),fill=INK)
d.line((s(bx+40),s(by+86),s(bx+SW-40),s(by+86)),fill=LINE,width=s(2))
bul=['練習時間を3条件で比較','条件ごとの正答率を測定','長いほど正答率が高い傾向','30分以上では差が小さい','個人差も大きかった']
for i,t in enumerate(bul):
    yy=by+116+i*50
    d.ellipse((s(bx+46),s(yy+11),s(bx+56),s(yy+21)),fill=SUB)
    d.text((s(bx+72),s(yy)),t,font=F(reg,25),fill=SUB)
# GOOD slide
gx,gy=828,200
badge(gx+20,160,True,'良い例','見出しは主張の文、本文は図')
slide(gx,gy,SW,SH)
d.text((s(gx+40),s(gy+26)),'練習を30分に延ばすと',font=F(bold,32),fill=INK)
d.text((s(gx+40),s(gy+68)),'正答率は約2倍になった',font=F(bold,32),fill=INK)
# bar chart
base=gy+SH-50; cx0=gx+120
vals=[('10分',38),('30分',76),('60分',82)]
maxh=200; bw=110; gap=70
for i,(lab,v) in enumerate(vals):
    x=cx0+i*(bw+gap); hh=maxh*v/100
    col=GOOD if i==1 else '#C9CDD3'
    d.rectangle((s(x),s(base-hh),s(x+bw),s(base)),fill=col)
    d.text((s(x+bw/2),s(base-hh-8)),f'{v}%',font=F(bold,24),fill=GOOD if i==1 else SUB,anchor='mb')
    d.text((s(x+bw/2),s(base+8)),lab,font=F(reg,22),fill=SUB,anchor='mt')
d.line((s(cx0-20),s(base),s(cx0+3*bw+2*gap+20),s(base)),fill=SUB,width=s(2))
d.text((s(gx+SW-20),s(gy+SH-14)),'架空のデータ',font=F(reg,16),fill=MUTE,anchor='rb')
# arrows / annotations under slides
ay=by+SH+40
def note(x,y,col,lines):
    for i,(t,f) in enumerate(lines):
        d.text((s(x),s(y+i*46)),t,font=f,fill=col if i==0 else SUB)
note(bx,ay,BAD,[('話題しか書かれていない',F(bold,28)),('何が言いたいのかを、聞き手が自分で探すことになる',F(reg,23))])
note(gx,ay,GOOD,[('1枚に1つの主張、それを示す証拠',F(bold,28)),('見出しを読むだけで、話の筋がたどれる',F(reg,23))])
# bottom band: evidence
yb=by+SH+160
d.rounded_rectangle((s(72),s(yb),s(1528),s(yb+150)),radius=s(14),fill='#FFFFFF')
d.text((s(108),s(yb+28)),'ルール',font=F(bold,26),fill=INK)
d.text((s(220),s(yb+28)),'見出しは2行以内の完全な文 ／ 本文は図・写真・グラフ ／ 文字はできるだけ少なく',font=F(reg,25),fill=INK)
d.text((s(108),s(yb+86)),'研究',font=F(bold,26),fill=INK)
d.text((s(220),s(yb+86)),'工学部生110人の比較実験で、理解度が高く誤解が少なかった（Garner & Alley, 2013）',font=F(reg,25),fill=INK)
img.save(str(__import__('pathlib').Path(__file__).resolve().parents[2].joinpath('images','005.png')))
print(img.size)
