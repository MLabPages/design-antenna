
from PIL import Image, ImageDraw, ImageFont
S=1.5
W,H=int(1600*S),int(900*S)
reg='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def F(p,z): return ImageFont.truetype(p,int(z*S),index=0)
def s(v): return int(v*S)
def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
img=Image.new('RGB',(W,H),'#F4F1EA'); d=ImageDraw.Draw(img)
INK='#1F2430'; MUTE='#6B6F78'; SUB='#4A4F59'
d.text((s(72),s(52)),'コントラスト比',font=F(bold,48),fill=INK)
tw=d.textlength('コントラスト比',font=F(bold,48))
d.text((s(72)+tw+s(22),s(70)),'Contrast Ratio — 本文は 4.5:1 以上',font=F(reg,26),fill=MUTE)
colw=(1600-72*2-56)/2
def fmt(r): return f'{r:.1f}:1'
def panel(x0,good):
    col='#2E7D6B' if good else '#C8553D'
    cy=172; r=20; cx=x0+20
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=col)
    mk='○' if good else '×'; f=F(bold,24); mw=d.textlength(mk,font=f)
    d.text((s(cx)-mw/2,s(cy)),mk,font=f,fill='white',anchor='lm')
    lab='良い例' if good else '悪い例'
    d.text((s(x0+54),s(cy)),lab,font=F(bold,30),fill=INK,anchor='lm')
    lw=d.textlength(lab,font=F(bold,30))
    d.text((s(x0+54)+lw+s(14),s(cy)),'濃い文字で、確実に読める' if good else '淡い灰色は、上品でも読めない',font=F(reg,26),fill=SUB,anchor='lm')
    top,bot=210,760
    d.rounded_rectangle((s(x0)+s(2),s(top)+s(4),s(x0+colw)+s(2),s(bot)+s(4)),radius=s(14),fill='#E6E2D9')
    d.rounded_rectangle((s(x0),s(top),s(x0+colw),s(bot)),radius=s(14),fill='white')
    bg='#FFFFFF'
    head = '#1F2430' if good else '#9AA0A8'
    body = '#4A4F59' if good else '#BBBFC5'
    px=x0+52; y=top+56
    d.text((s(px),s(y)),'研究の背景',font=F(bold,44),fill=head); y+=92
    for line in ['淡い灰色の文字は','上品に見えても','読めなければ伝わらない']:
        d.text((s(px),s(y)),line,font=F(reg,34),fill=body); y+=58
    # badges
    y=top+430
    for name,c,th in [('見出し',head,3.0),('本文',body,4.5)]:
        rr=ratio(c,bg); ok = rr>=th
        bc='#2E7D6B' if ok else '#C8553D'
        d.text((s(px),s(y)),name,font=F(reg,26),fill=SUB,anchor='lm')
        d.rounded_rectangle((s(px+110),s(y-12),s(px+142),s(y+20)),radius=s(6),fill=c,outline='#D5D8DD',width=s(1))
        d.text((s(px+164),s(y)),fmt(rr),font=F(bold,32),fill=bc,anchor='lm')
        rw=d.textlength(fmt(rr),font=F(bold,32))
        d.text((s(px+164)+rw+s(16),s(y)),'基準を満たす' if ok else (f'{th:g}:1 に届かない'),font=F(reg,24),fill=bc,anchor='lm')
        y+=60
    print(good, head, fmt(ratio(head,bg)), body, fmt(ratio(body,bg)))
panel(72,False); panel(72+colw+56,True)
note='WCAG 2.2（AA）の基準：本文 4.5:1 以上／大きな文字（18pt、太字なら14pt）は 3:1 以上'
f=F(reg,25); nw=d.textlength(note,font=f)
d.text((s(800)-nw/2,s(800)),note,font=f,fill=SUB)
img.save('images/002.png',optimize=True)
print(img.size)
