import colorsys
import hashlib
import os
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

from celery_app import celery_app

MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")
AVATAR_SIZE = 256

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()


def _hsl_to_rgb(hue_deg: float, saturation: float, lightness: float) -> tuple:
    r, g, b = colorsys.hls_to_rgb((hue_deg % 360) / 360, lightness, saturation)
    return (int(r * 255), int(g * 255), int(b * 255))


def _gradient_colors(digest: str) -> tuple:
    hue1 = int(digest[0:4], 16) % 360
    hue2 = int(digest[4:8], 16) % 360
    if abs(hue1 - hue2) < 40:
        hue2 = (hue2 + 90) % 360

    color1 = _hsl_to_rgb(hue1, 0.65, 0.55)
    color2 = _hsl_to_rgb(hue2, 0.65, 0.40)
    return color1, color2


def _diagonal_gradient(size: int, color1: tuple, color2: tuple) -> Image.Image:
    base = Image.new("RGB", (size, size), color1)
    top = Image.new("RGB", (size, size), color2)

    mask = Image.new("L", (size, size))
    mask_data = [
        int((x + y) / (2 * (size - 1)) * 255)
        for y in range(size)
        for x in range(size)
    ]
    mask.putdata(mask_data)

    return Image.composite(top, base, mask)


def _add_pattern(image: Image.Image, digest: str) -> Image.Image:
    size = image.size[0]
    values = [int(digest[i : i + 2], 16) for i in range(8, 24, 2)]

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for i in range(3):
        vx = values[i % len(values)]
        vy = values[(i + 1) % len(values)]
        vr = values[(i + 2) % len(values)]
        valpha = values[(i + 3) % len(values)]

        cx = int(vx / 255 * size)
        cy = int(vy / 255 * size)
        radius = int(size * 0.15 + (vr / 255) * size * 0.2)
        alpha = 25 + int(valpha / 255 * 35)

        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, 255, 255, alpha),
        )

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def _load_font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


@celery_app.task(name="tasks.generate_avatar")
def generate_avatar(name: str) -> dict:
    # Имитация длительной обработки — генерация вынесена в отдельный worker-сервис.
    time.sleep(2)

    os.makedirs(MEDIA_DIR, exist_ok=True)

    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    initials = _initials(name)
    color1, color2 = _gradient_colors(digest)

    image = _diagonal_gradient(AVATAR_SIZE, color1, color2)
    image = _add_pattern(image, digest)

    draw = ImageDraw.Draw(image)
    font = _load_font(AVATAR_SIZE // 2)
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = (
        (AVATAR_SIZE - text_w) / 2 - bbox[0],
        (AVATAR_SIZE - text_h) / 2 - bbox[1],
    )
    shadow_offset = 2
    draw.text(
        (position[0] + shadow_offset, position[1] + shadow_offset),
        initials,
        fill=(0, 0, 0, 90),
        font=font,
    )
    draw.text(position, initials, fill="white", font=font)

    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(MEDIA_DIR, filename)
    image.convert("RGB").save(filepath, format="PNG")

    return {"filename": filename}
