"""
HANS OptiCore – Name Board → 2ft-wide TIFF Generator
=====================================================
Generates a print-ready TIFF of the name board HTML at 2 feet width (300 DPI).

2 feet = 24 inches → 24 × 300 = 7200 px wide
Original aspect ratio is 1920:720 (8:3), so height = 7200 × (720/1920) = 2700 px
Final TIFF: 7200 × 2700 px @ 300 DPI → prints at exactly 24" × 9"

Usage:
    python generate_nameboard_2ft.py

Output: public/print-assets/tiff/nameboard-2ft.tiff
        public/print-assets/tiff/nameboard-2ft.png
"""

import sys
import shutil
from pathlib import Path

try:
    from html2image import Html2Image
except ImportError:
    print("ERROR: html2image not installed. Run: pip install html2image")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PRINT_ASSETS_DIR = SCRIPT_DIR / "public" / "print-assets"
HTML_FILE = PRINT_ASSETS_DIR / "name-board.html"
TIFF_OUTPUT_DIR = PRINT_ASSETS_DIR / "tiff"
TEMP_DIR = SCRIPT_DIR / "_temp_nameboard_2ft"

# ── Print dimensions ──────────────────────────────────
# 2 feet wide = 24 inches at 300 DPI = 7200 px
# Height keeps original 8:3 ratio → 2700 px (9 inches)
TARGET_WIDTH = 7200
TARGET_HEIGHT = 2700
DPI = 300

# Screenshot viewport — we render at a high resolution
# Using device scale factor 2x on a 3600×1350 viewport → 7200×2700 output
VIEWPORT_WIDTH = 3600
VIEWPORT_HEIGHT = 1350
SCALE_FACTOR = 2


def ensure_dirs():
    TIFF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def fix_paths(html_content: str) -> str:
    """Replace relative paths with absolute file:// URLs."""
    public_dir = SCRIPT_DIR / "public"
    replacements = {
        'src="../logo_og.png"': f'src="file:///{(public_dir / "logo_og.png").as_posix()}"',
        'src="../logo_wht.png"': f'src="file:///{(public_dir / "logo_wht.png").as_posix()}"',
        'src="../logo_grey.png"': f'src="file:///{(public_dir / "logo_grey.png").as_posix()}"',
        'src="logo_og.png"': f'src="file:///{(public_dir / "logo_og.png").as_posix()}"',
        'src="logo_wht.png"': f'src="file:///{(public_dir / "logo_wht.png").as_posix()}"',
    }
    for old, new in replacements.items():
        html_content = html_content.replace(old, new)

    # Fix font paths
    for font_file in ["NotoSansKannada-Regular.ttf", "NotoSansKannada-Bold.ttf"]:
        abs_path = PRINT_ASSETS_DIR / font_file
        for prefix in ["", "../"]:
            html_content = html_content.replace(
                f"url('{prefix}{font_file}')",
                f"url('file:///{abs_path.as_posix()}')"
            )
    return html_content


def generate():
    print("=" * 60)
    print("  HANS OptiCore – Name Board → 2ft TIFF Generator")
    print("=" * 60)

    if not HTML_FILE.exists():
        print(f"\nERROR: {HTML_FILE} not found!")
        sys.exit(1)

    ensure_dirs()

    html_content = HTML_FILE.read_text(encoding="utf-8")
    html_content = fix_paths(html_content)

    print(f"\n  Source:     {HTML_FILE.name}")
    print(f"  Viewport:   {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT} @ {SCALE_FACTOR}x scale")
    print(f"  Output:     {TARGET_WIDTH}x{TARGET_HEIGHT} px")
    print(f"  Print size: 24\" x 9\" (2ft x 0.75ft) @ {DPI} DPI")

    # ── Step 1: Screenshot at high resolution ──
    print("\n  [1/3] Rendering HTML → PNG ...")
    hti = Html2Image(
        output_path=str(TEMP_DIR),
        custom_flags=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--hide-scrollbars",
            f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}",
            f"--force-device-scale-factor={SCALE_FACTOR}",
        ],
    )
    hti.size = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

    png_name = "nameboard-2ft-raw.png"
    hti.screenshot(html_str=html_content, save_as=png_name)

    raw_png = TEMP_DIR / png_name
    if not raw_png.exists():
        print("  ERROR: Failed to generate PNG screenshot")
        sys.exit(1)

    # ── Step 2: Resize to exact target dimensions ──
    print("  [2/3] Resizing to exact 7200x2700 ...")
    img = Image.open(raw_png)
    print(f"         Raw screenshot: {img.width}x{img.height}")

    if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    # Convert RGBA → RGB
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    # Save final PNG
    png_output = TIFF_OUTPUT_DIR / "nameboard-2ft.png"
    img.save(str(png_output), dpi=(DPI, DPI))
    print(f"         Saved PNG: {png_output.name}")

    # ── Step 3: Convert to TIFF ──
    print("  [3/3] Converting to TIFF @ 300 DPI ...")
    tiff_output = TIFF_OUTPUT_DIR / "nameboard-2ft.tiff"
    img.save(
        str(tiff_output),
        format="TIFF",
        dpi=(DPI, DPI),
        compression="tiff_lzw",
    )
    print(f"         Saved TIFF: {tiff_output.name}")

    # ── Cleanup ──
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f"\n  Output files:")
    print(f"    PNG  → {png_output}")
    print(f"    TIFF → {tiff_output}")
    print(f"\n  Print dimensions: 24\" wide x 9\" tall (2 feet x 0.75 feet)")
    print(f"  Resolution: {DPI} DPI")
    print("=" * 60)


if __name__ == "__main__":
    generate()
