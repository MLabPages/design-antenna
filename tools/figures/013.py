from PIL import Image, ImageDraw, ImageFont
# 第13回 類同の法則（Law of Similarity） 図。PILで描画。配色は Okabe–Ito を使用
S=1.5
BW,BH=1600,1110
W,H=int(BW*S),int(BH*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(round(v*S))
BG='#F4F1EA'; INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'; BAD='#C8553D'; GOOD='#2E7D6B'; LINE='#D9D4CA'
# Okabe–Ito
OI_ORANGE='#E69F00'; OI_SKY='#56B4E9'; OI_GREEN='#009E73'; OI_YELLOW='#F0E442'; OI_BLUE='#0072B2'; OI_VERM='#D55E00'; OI_PURPLE='#CC79A7'
GRAY='#BFC3CA'
img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
d.text((s(72),s(44)),'類同の法則',font=F(bold,50),fill=INK)
tw=d.textlength('類同の法則',font=F(bold,50))
d.text((s(72)+tw+s(24),s(68)),'Law of Similarity ─ 色・形・大きさが似たものは、同じ仲間に見える',font=F(reg,26),fill=MUTE)

def card(x,y,w,h,outline=LINE,width=2):
    d.rounded_rectangle((s(x)+s(3),s(y)+s(5),s(x+w)+s(3),s(y+h)+s(5)),radius=s(12),fill='#E3DED4')
    d.rounded_rectangle((s(x),s(y),s(x+w),s(y+h)),radius=s(12),fill='white',outline=outline,width=s(width))

def dot(cx,cy,r,col):
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=col)

# ---- 上段：しくみ（2枚）
TY=150; TH=330; TW=713; GAP=30
heads=[('等間隔でも、同じ色の列にまとまる','見た目が似たもの同士が「仲間」になる'),
       ('1つだけ違うと、すぐ目に入る','似ていないものは、仲間から浮いて目立つ')]
for k,(h1,h2) in enumerate(heads):
    x=72+k*(TW+GAP)
    card(x,TY,TW,TH)
    d.text((s(x+32),s(TY+42)),h1,font=F(bold,28),fill=INK,anchor='lm')
    # grid
    cols,rows=7,4; step=50; r=15
    gw=(cols-1)*step; gx=x+(TW-gw)/2; gy=TY+104
    for i in range(cols):
        for j in range(rows):
            cx=gx+i*step; cy=gy+j*step
            if k==0: col=OI_BLUE if i%2==0 else OI_ORANGE
            else: col=OI_VERM if (i,j)==(4,1) else GRAY
            dot(cx,cy,r,col)
    d.text((s(x+TW/2),s(TY+TH-34)),h2,font=F(reg,23),fill=SUB,anchor='mm')

# ---- 下段：グラフでの悪い例／良い例
def badge(x,y,good,lab,sub):
    col=GOOD if good else BAD; r=20
    d.ellipse((s(x-r),s(y-r),s(x+r),s(y+r)),fill=col)
    if good: d.ellipse((s(x-9),s(y-9),s(x+9),s(y+9)),outline='white',width=s(4))
    else:
        d.line((s(x-8),s(y-8),s(x+8),s(y+8)),fill='white',width=s(4)); d.line((s(x-8),s(y+8),s(x+8),s(y-8)),fill='white',width=s(4))
    d.text((s(x+34),s(y)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x+34)+lw+s(12),s(y+2)),sub,font=F(reg,22),fill=SUB,anchor='lm')

BY=TY+TH+110; BHh=470
labels=['A','B','C','D','E','提案']
vals=[52,58,49,61,55,74]
bad_cols=[OI_ORANGE,OI_SKY,OI_GREEN,OI_YELLOW,OI_PURPLE,OI_BLUE]
panels=[(False,'色がばらばら','どれが大事か分からない',bad_cols,'色に意味がなく、目が迷う'),
        (True,'仲間は同じ色','強調は1本だけ',[GRAY]*5+[OI_VERM],'見せたい1本がすぐ分かる')]
for k,(good,lab,sub,cols_,note) in enumerate(panels):
    x=72+k*(TW+GAP)
    badge(x+20,BY-46,good,lab,sub)
    card(x,BY,TW,BHh,outline=(GOOD if good else LINE),width=(3 if good else 2))
    # axes
    ax0=x+90; ax1=x+TW-50; ay0=BY+50; ay1=BY+BHh-130
    d.line((s(ax0),s(ay1),s(ax1),s(ay1)),fill='#9AA0A8',width=s(2))
    n=len(vals); slot=(ax1-ax0)/n; bw=slot*0.58
    vmax=80
    for i,(lb,v) in enumerate(zip(labels,vals)):
        cx=ax0+slot*(i+0.5)
        top=ay1-(ay1-ay0)*v/vmax
        d.rectangle((s(cx-bw/2),s(top),s(cx+bw/2),s(ay1)),fill=cols_[i])
        hl=(good and i==n-1)
        d.text((s(cx),s(ay1+30)),lb,font=F(bold if hl else reg,26),fill=(INK if (hl or not good) else MUTE),anchor='mm')
        if hl:
            d.text((s(cx),s(top-24)),str(v),font=F(bold,28),fill=OI_VERM,anchor='mm')
    d.line((s(x+28),s(BY+BHh-70),s(x+TW-28),s(BY+BHh-70)),fill='#EEF0F2',width=s(1))
    d.text((s(x+TW/2),s(BY+BHh-36)),note,font=F(reg,24),fill=(GOOD if good else BAD),anchor='mm')

img=img.resize((BW,BH),Image.LANCZOS)
img.save('images/013.png',optimize=True)
