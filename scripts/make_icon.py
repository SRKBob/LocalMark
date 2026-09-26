"""Generate LocalMark app icon (rounded-square gradient + LM mark) -> build/icon.ico"""
from PIL import Image, ImageDraw, ImageFont

SIZE = 512
SS = 4  # supersample factor for smooth edges
W = SIZE * SS

# --- gradient background ---
grad = Image.new("RGB", (W, W))
gd = ImageDraw.Draw(grad)
c1 = (37, 99, 235)    # blue-600
c2 = (79, 70, 229)    # indigo-600
for y in range(W):
    t = y / (W - 1)
    gd.line(
        [(0, y), (W, y)],
        fill=(
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        ),
    )

# --- rounded-square mask ---
mask = Image.new("L", (W, W), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, W - 1], radius=int(W * 0.22), fill=255)

icon = Image.new("RGBA", (W, W), (0, 0, 0, 0))
icon.paste(grad, (0, 0), mask)

# --- subtle top-left sheen ---
sheen = Image.new("RGBA", (W, W), (0, 0, 0, 0))
sd = ImageDraw.Draw(sheen)
sd.ellipse([-int(W * 0.35), -int(W * 0.55), int(W * 0.95), int(W * 0.45)],
           fill=(255, 255, 255, 38))
icon = Image.alpha_composite(icon, Image.composite(sheen, Image.new("RGBA", (W, W), (0, 0, 0, 0)), mask))

# --- "LM" text ---
draw = ImageDraw.Draw(icon)
font_path = "C:/Windows/Fonts/arialbd.ttf"
font = ImageFont.truetype(font_path, int(W * 0.42))
text = "LM"
bbox = draw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
pos = ((W - tw) / 2 - bbox[0], (W - th) / 2 - bbox[1] - int(W * 0.045))

# drop shadow for legibility
shadow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((pos[0] + int(W * 0.012), pos[1] + int(W * 0.018)), text,
                            font=font, fill=(15, 23, 42, 90))
icon = Image.alpha_composite(icon, shadow)

draw = ImageDraw.Draw(icon)
draw.text(pos, text, font=font, fill=(255, 255, 255, 255))

# --- underline accent bar ---
bar_w, bar_h = int(W * 0.30), int(W * 0.045)
bx, by = (W - bar_w) / 2, W * 0.735
draw.rounded_rectangle([bx, by, bx + bar_w, by + bar_h], radius=bar_h // 2,
                       fill=(147, 197, 253, 255))

icon = icon.resize((SIZE, SIZE), Image.LANCZOS)

icon.save("build/icon.png")
icon.save(
    "build/icon.ico",
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("icon.png / icon.ico generated")
