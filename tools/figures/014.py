from PIL import Image, ImageDraw, ImageFont
# 第14回 チャンク化（Chunking） 図。PILで描画。配色は Okabe–Ito を使用
S=1.5
BW,BH=1600,1110
W,H=int(BW*S),int(BH*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'; INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'
OI_ORANGE='#E69F00'; OI_SKY='#56B4E9'; OI_GREEN='#009E73'; OI_BLUE='#0072B2'; OI_VERM='#D55E00'; OI_PURPLE='#CC79A7'
GRAY='#C9CDD3'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
d.text((s(72),s(44)),'チャンク化',font=F(bold,50),fill=INK)
tw=d.textlength('チャンク化',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Chunking ─ 意味のあるまとまりに分けると、読みやすく覚えやすい',font=F(reg,26),fill=MUTE)

def card(x,y,w,h,outline=LINE,width=2):
    d.rounded_rectangle((s(x)+s(3),s(y)+s(5),s(x+w)+s(3),s(y+h)+s(5)),radius=s(12),fill='#E3DED4')
    d.rounded_rectangle((s(x),s(y),s(x+w),s(y+h)),radius=s(12),fill='white',outline=outline,width=s(width))

def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(12),s(y+2)),sub,font=F(reg,22),fill=SUB,anchor='lm')

TW=713; GAP=30
BADY=176
badge(72+20,BADY,False,'区切りなし','ひと続きのかたまり')
badge(72+TW+GAP+20,BADY,True,'まとまりに分ける','3〜4個ずつ、見出しつき')

# ---- 上段：番号
TY=226; TH=230
for k in range(2):
    good=(k==1); x=72+k*(TW+GAP)
    card(x,TY,TW,TH,outline=(GOOD if good else LINE),width=(3 if good else 2))
    d.text((s(x+32),s(TY+40)),'電話番号',font=F(bold,26),fill=SUB,anchor='lm')
    cy=TY+122
    if not good:
        d.text((s(x+TW/2),s(cy)),'09012345678',font=F(bold,60),fill=INK,anchor='mm')
        d.text((s(x+TW/2),s(TY+TH-36)),'11桁を1つずつ覚えることになる',font=F(reg,23),fill=BAD,anchor='mm')
    else:
        parts=['090','1234','5678']; f=F(bold,60)
        ws=[d.textlength(p,font=f) for p in parts]; gap=s(44)
        total=sum(ws)+gap*2; cx=s(x+TW/2)-total/2
        for i,(p,w) in enumerate(zip(parts,ws)):
            d.rounded_rectangle((cx-s(12),s(cy-40),cx+w+s(12),s(cy+42)),radius=s(10),fill='#E6F2EE')
            d.text((cx,s(cy)),p,font=f,fill=INK,anchor='lm')
            cx+=w+gap
        d.text((s(x+TW/2),s(TY+TH-36)),'3つのかたまりなら、すっと読める',font=F(reg,23),fill=GOOD,anchor='mm')

# ---- 下段：スライドの箇条書き
BY=TY+TH+40; BHh=H/S-BY-60
lens=[0.86,0.62,0.78,0.55,0.90,0.70,0.66,0.82,0.58,0.74,0.64,0.80]
for k in range(2):
    good=(k==1); x=72+k*(TW+GAP)
    card(x,BY,TW,BHh,outline=(GOOD if good else LINE),width=(3 if good else 2))
    d.text((s(x+32),s(BY+40)),'スライドの箇条書き（12項目）',font=F(bold,26),fill=SUB,anchor='lm')
    top=BY+84; bottom=BY+BHh-80
    if not good:
        n=12; step=(bottom-top)/n
        for i in range(n):
            y=top+step*(i+0.5)
            d.ellipse((s(x+52-6),s(y-6),s(x+52+6),s(y+6)),fill='#9AA0A8')
            d.rounded_rectangle((s(x+74),s(y-8),s(x+74+(TW-140)*lens[i]),s(y+8)),radius=s(8),fill=GRAY)
        note='どこで区切るか分からず、全体がつかめない'
    else:
        groups=[('背景',OI_BLUE),('方法',OI_VERM),('結果',OI_GREEN)]
        cols=3; gw=(TW-64-2*24)/cols
        for g,(lab,col) in enumerate(groups):
            gx=x+32+g*(gw+24); gy=top+6; gh=bottom-top-6
            d.rounded_rectangle((s(gx),s(gy),s(gx+gw),s(gy+gh)),radius=s(10),fill='#F7F6F2')
            d.rounded_rectangle((s(gx),s(gy),s(gx+gw),s(gy+60)),radius=s(10),fill=col)
            d.rectangle((s(gx),s(gy+40),s(gx+gw),s(gy+60)),fill=col)
            d.text((s(gx+gw/2),s(gy+30)),lab,font=F(bold,28),fill='white',anchor='mm')
            for i in range(4):
                y=gy+60+(gh-60)*(i+0.5)/4
                d.ellipse((s(gx+22-6),s(y-6),s(gx+22+6),s(y+6)),fill=col)
                L=lens[g*4+i]
                d.rounded_rectangle((s(gx+40),s(y-8),s(gx+40+(gw-62)*L),s(y+8)),radius=s(8),fill=GRAY)
        note='見出しで3つに分け、各4項目。全体がひと目で分かる'
    d.line((s(x+28),s(BY+BHh-62),s(x+TW-28),s(BY+BHh-62)),fill='#EEF0F2',width=s(1))
    d.text((s(x+TW/2),s(BY+BHh-32)),note,font=F(reg,24),fill=(GOOD if good else BAD),anchor='mm')

img=img.resize((BW,BH),Image.LANCZOS)
img.save('images/014.png',optimize=True)
