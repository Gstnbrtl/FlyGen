from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
PHOTOS_DIR  = BASE_DIR / "assets" / "photos"
FONTS_DIR   = BASE_DIR / "assets" / "fonts"
OUTPUT_DIR  = BASE_DIR / "output"

# ── Brand ───────────────────────────────────────────────────────────────────
BRAND_NAME  = "NEGRO PADEL"
WHATSAPP    = "+54 9 358 429-4011"
INSTAGRAM   = "@negropadel"

# ── Colors (RGB) ────────────────────────────────────────────────────────────
COLOR_BG        = (9,   9,  15)      # almost black
COLOR_SURFACE   = (19,  19, 28)      # dark card
COLOR_GREEN     = (48, 209, 88)      # disponible green
COLOR_WHITE     = (255, 255, 255)
COLOR_GRAY      = (160, 160, 170)
COLOR_OVERLAY   = (0,   0,   0, 215) # RGBA — dark photo overlay

# ── Canvas ──────────────────────────────────────────────────────────────────
CANVAS_SIZE = (1080, 1920)

# ── Fonts (Windows system fonts — always available) ──────────────────────────
FONT_HEADLINE = "C:/Windows/Fonts/impact.ttf"        # big bold headline
FONT_BODY     = "C:/Windows/Fonts/arialbd.ttf"       # slot rows
FONT_SMALL    = "C:/Windows/Fonts/arial.ttf"         # date / footer

# ── Gemini model (gratis) ───────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash-lite"
