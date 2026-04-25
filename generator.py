import random
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import (
    PHOTOS_DIR, OUTPUT_DIR,
    CANVAS_SIZE, FONT_BODY, FONT_SMALL, FONTS_DIR,
)

DAYS_ES   = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
MONTHS_ES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

COLOR_ORANGE = (255, 110, 0)
COLOR_WHITE  = (255, 255, 255)
COLOR_GRAY   = (180, 180, 180)

# El espacio negro del background empieza aprox al 62% de la altura
DAY_RATIO    = 0.535  # centro entre las dos líneas naranjas del background
SLOTS_RATIO  = 0.615  # donde empiezan los horarios


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _pick_background() -> tuple[Image.Image, tuple[int,int]] | tuple[None, tuple[int,int]]:
    exts   = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.jfif")
    photos = [p for ext in exts for p in PHOTOS_DIR.rglob(ext)]
    if not photos:
        return None, CANVAS_SIZE
    img  = Image.open(random.choice(photos)).convert("RGB")
    size = (img.width, img.height)
    return img, size


def _center_x(draw, text, font, canvas_w):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (canvas_w - (bbox[2] - bbox[0])) // 2


def generate_flyer(slots: list, target_date: date = None) -> Path:
    if target_date is None:
        target_date = date.today()

    bg, (W, H) = _pick_background()
    canvas = bg if bg else Image.new("RGB", (W, H), (9, 9, 15))
    draw = ImageDraw.Draw(canvas)

    barlow = str(FONTS_DIR / "BarlowCondensed-ExtraBoldItalic.ttf")
    f_day  = _load_font(FONT_BODY, 72)
    f_time = _load_font(barlow, 110)

    # ── Día centrado entre las líneas naranjas del background ──
    day_str = DAYS_ES[target_date.weekday()].upper()
    bbox    = draw.textbbox((0, 0), day_str, font=f_day)
    text_h  = bbox[3] - bbox[1]
    day_y   = int(H * DAY_RATIO) - text_h // 2
    draw.text((_center_x(draw, day_str, f_day, W), day_y),
              day_str, font=f_day, fill=COLOR_WHITE)

    # ── Horarios: 1 columna si <=3, 2 columnas si >3 ──
    card_gap = 30
    bbox_h   = lambda t: draw.textbbox((0,0), t, font=f_time)[3] - draw.textbbox((0,0), t, font=f_time)[1]
    slot_y   = int(H * SLOTS_RATIO)

    if len(slots) <= 3:
        y = slot_y
        for slot in slots:
            draw.text((_center_x(draw, slot['time'], f_time, W), y),
                      slot['time'], font=f_time, fill=COLOR_ORANGE)
            y += bbox_h(slot['time']) + card_gap
    else:
        col_w       = W // 2
        mid         = len(slots) // 2 + len(slots) % 2
        left_slots  = slots[:mid]
        right_slots = slots[mid:]
        for col_slots, col_x in [(left_slots, 0), (right_slots, col_w)]:
            y = slot_y
            for slot in col_slots:
                bb = draw.textbbox((0, 0), slot['time'], font=f_time)
                tw = bb[2] - bb[0]
                draw.text((col_x + (col_w - tw) // 2, y),
                          slot['time'], font=f_time, fill=COLOR_ORANGE)
                y += bbox_h(slot['time']) + card_gap

    # ── "Últimos turnos disponibles!" si quedan 1 o 2 ──
    if len(slots) <= 2:
        barlow = str(FONTS_DIR / "BarlowCondensed-ExtraBoldItalic.ttf")
        f_urgente = _load_font(barlow, 58)
        texto = "Ultimos turnos disponibles!"
        draw.text(
            (_center_x(draw, texto, f_urgente, W), y + 20),
            texto, font=f_urgente, fill=COLOR_WHITE
        )

    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = OUTPUT_DIR / f"flyer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    canvas.save(filename, "PNG")
    return filename
