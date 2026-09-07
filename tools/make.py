from PIL import Image, ImageDraw, ImageFont
import os, sys

SP = os.path.dirname(os.path.abspath(__file__))
FONT = "/System/Library/Fonts/Supplemental/Songti.ttc"

# 页面调色板 (藍紙金泥寫經)
TOP    = (23, 33, 61)     # #17213D
BOT    = (13, 20, 36)     # #0D1424
GOLD   = (210, 172, 88)   # #D2AC58
VERM   = (220, 97, 70)    # #DC6146

def pick_face():
    """必須實際渲染後統計像素: 缺字時 getbbox 也會回非零寬度, 會選到空字面"""
    best = (None, 0)
    for i in range(0, 12):
        try:
            f = ImageFont.truetype(FONT, 300, index=i)
        except Exception:
            break
        im = Image.new("L", (400, 400), 0)
        ImageDraw.Draw(im).text((50, 30), "彌", font=f, fill=255)
        px = sum(1 for v in im.tobytes() if v > 40)
        if px > best[1]: best = (i, px)
    if best[0] is None: raise RuntimeError("找不到可用字面")
    print(f"  字面 index={best[0]} 渲染 {best[1]} 像素")
    return best[0]

FACE = pick_face()
print("Songti.ttc 使用字面 index =", FACE)

def draw_icon(S, char_ratio=0.56, dot=True):
    """S = 边长; char_ratio = 字高占比 (maskable 版留更多余白)"""
    im = Image.new("RGB", (S, S))
    d  = ImageDraw.Draw(im)
    for y in range(S):                                  # 竖向渐变
        t = y / max(1, S - 1)
        d.line([(0, y), (S, y)],
               fill=tuple(round(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)))

    # 金色「彌」—— 用 bbox 精确居中
    size = int(S * char_ratio * 1.18)
    f = ImageFont.truetype(FONT, size, index=FACE)
    bb = f.getbbox("彌")
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
    cy = S * (0.545 if dot else 0.50)                   # 有点时字略下移, 给点留位置
    d.text((S/2 - cw/2 - bb[0], cy - ch/2 - bb[1]), "彌", font=f, fill=GOLD)

    if dot:                                             # 简谱高八度点
        r = S * 0.038
        cx, dy = S/2, cy - ch/2 - r*2.35
        d.ellipse([cx-r, dy-r, cx+r, dy+r], fill=VERM)
    return im

# 小尺寸專用: 「彌」有十七筆, 32px 以下必糊, 改用簡譜的 5̣ (本曲第一個音)
SANS = [ "/System/Library/Fonts/Helvetica.ttc",
         "/System/Library/Fonts/HelveticaNeue.ttc",
         "/System/Library/Fonts/Supplemental/Arial.ttf" ]
def pick_sans():
    for path in SANS:
        if not os.path.exists(path): continue
        for i in range(0, 6):
            try: f = ImageFont.truetype(path, 200, index=i)
            except Exception: break
            im = Image.new("L", (300, 300), 0)
            ImageDraw.Draw(im).text((40, 20), "5", font=f, fill=255)
            if sum(1 for v in im.tobytes() if v > 40) > 500: return path, i
    return None, 0
SANS_PATH, SANS_IDX = pick_sans()
print("  小尺寸字体:", os.path.basename(SANS_PATH or "無"), "index", SANS_IDX)

def draw_small(S):
    im = Image.new("RGB", (S, S)); d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / max(1, S - 1)
        d.line([(0, y), (S, y)],
               fill=tuple(round(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)))
    f = ImageFont.truetype(SANS_PATH, int(S * 0.72), index=SANS_IDX)
    bb = f.getbbox("5"); cw, ch = bb[2]-bb[0], bb[3]-bb[1]
    cy = S * 0.455
    d.text((S/2 - cw/2 - bb[0], cy - ch/2 - bb[1]), "5", font=f, fill=GOLD)
    r = max(1.0, S * 0.075)                       # 低八度點
    dy = cy + ch/2 + r*1.5
    d.ellipse([S/2-r, dy-r, S/2+r, dy+r], fill=VERM)
    return im

base = draw_icon(1024)
base.save(f"{SP}/icon-1024.png")

# 大尺寸 (主屏幕 / Dock): 彌 + 高八度點
for s in (512, 192, 180, 167, 152, 120, 96, 64):
    base.resize((s, s), Image.LANCZOS).save(f"{SP}/icon-{s}.png")

# 小尺寸 (瀏覽器頁籤): 5̣
for s in (48, 32, 16):
    draw_small(s * 8).resize((s, s), Image.LANCZOS).save(f"{SP}/icon-{s}.png")

# Android 自适应图标: 设计需落在中央 80% 圆内, 所以字更小、余白更多
draw_icon(1024, char_ratio=0.42).resize((512, 512), Image.LANCZOS).save(f"{SP}/icon-maskable-512.png")

print("已生成:", ", ".join(sorted(os.listdir(SP))))
