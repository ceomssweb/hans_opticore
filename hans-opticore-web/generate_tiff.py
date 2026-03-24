"""
HANS OptiCore – HTML to TIFF Converter
=======================================
Converts all print-asset HTML files to high-resolution TIFF images.
Uses html2image (Chrome/Chromium) for HTML→PNG, then Pillow for PNG→TIFF.

Usage:
    python generate_tiff.py

Output folder: public/print-assets/tiff/
"""

import os
import sys
import glob
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

from PIL import ImageChops


# ── Paths ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PRINT_ASSETS_DIR = SCRIPT_DIR / "public" / "print-assets"
LIGHT_DIR = PRINT_ASSETS_DIR / "light"
TIFF_OUTPUT_DIR = PRINT_ASSETS_DIR / "tiff"
TEMP_DIR = SCRIPT_DIR / "_temp_screenshots"

# ── Image dimensions for each element ──────────────────
# (filename_pattern, element_label, width, height)
CAPTURE_MAP = [
    # Dark themed
    ("visiting-card.html",  "visiting-card-dark-front1",  1050, 600),
    ("visiting-card.html",  "visiting-card-dark-front2",  1050, 600),
    ("visiting-card.html",  "visiting-card-dark-back",    1050, 600),
    ("letterhead.html",     "letterhead-dark",            794,  1123),
    ("banner.html",         "banner-dark-rollup",         500,  1500),
    ("banner.html",         "banner-dark-horizontal",     1200, 400),
    ("banner.html",         "banner-dark-tabletop",       900,  280),
    # Light themed
    ("light/visiting-card-light.html", "visiting-card-light-front1", 1050, 600),
    ("light/visiting-card-light.html", "visiting-card-light-front2", 1050, 600),
    ("light/visiting-card-light.html", "visiting-card-light-back",   1050, 600),
    ("light/letterhead-light.html",    "letterhead-light",           794,  1123),
    ("light/banner-light.html",        "banner-light-rollup",        500,  1500),
    ("light/banner-light.html",        "banner-light-horizontal",    1200, 400),
    ("light/banner-light.html",        "banner-light-tabletop",      900,  280),
    # Name boards – Dark
    ("name-board.html",                "name-board-dark-main",       1920, 720),
    ("name-board.html",                "name-board-dark-compact",    1440, 480),
    ("name-board.html",                "name-board-dark-vertical",   480,  1280),
    ("name-board.html",                "name-board-dark-glow",       2400, 720),
    ("name-board.html",                "name-board-dark-light-theme",1920, 720),
    # Name boards – Light
    ("light/name-board-light.html",    "name-board-light-main",      1920, 720),
    ("light/name-board-light.html",    "name-board-light-compact",   1440, 480),
    ("light/name-board-light.html",    "name-board-light-vertical",  480,  1280),
    ("light/name-board-light.html",    "name-board-light-glow",      2400, 720),
    # Name board – OG (original)
    ("nameboard-og/name-board.html",   "nameboard-og",               2500, 5000),
]

# For full-page screenshots we use conservative page sizes
PAGE_SIZES = {
    "visiting-card.html":              (1200, 2200),
    "letterhead.html":                 (900,  1300),
    "banner.html":                     (1400, 3000),
    "light/visiting-card-light.html":  (1200, 2200),
    "light/letterhead-light.html":     (900,  1300),
    "light/banner-light.html":         (1400, 3000),
    "name-board.html":                 (2500, 5000),
    "light/name-board-light.html":     (2500, 4000),
    "nameboard-og/name-board.html":     (2500, 5000),
}

DPI = 300


def ensure_dirs():
    """Create output directories."""
    TIFF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def html_to_png(html_file: str, output_name: str, size: tuple) -> Path:
    """Render an HTML file to a PNG screenshot."""
    html_path = PRINT_ASSETS_DIR / html_file
    if not html_path.exists():
        print(f"  ⚠ Skipping {html_file} – file not found")
        return None

    w, h = size
    hti = Html2Image(
        output_path=str(TEMP_DIR),
        custom_flags=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--hide-scrollbars",
            f"--window-size={w},{h}",
        ],
    )
    hti.size = (w, h)

    png_name = f"{output_name}.png"

    # Read HTML content and fix relative paths to use absolute file:// URLs
    html_content = html_path.read_text(encoding="utf-8")

    # Replace relative logo paths with absolute paths
    public_dir = SCRIPT_DIR / "public"
    logo_og_abs = public_dir / "logo_og.png"
    logo_wht_abs = public_dir / "logo_wht.png"
    logo_grey_abs = public_dir / "logo_grey.png"

    html_content = html_content.replace(
        'src="../logo_og.png"',
        f'src="file:///{logo_og_abs.as_posix()}"'
    )
    html_content = html_content.replace(
        'src="../logo_wht.png"',
        f'src="file:///{logo_wht_abs.as_posix()}"'
    )
    html_content = html_content.replace(
        'src="../logo_grey.png"',
        f'src="file:///{logo_grey_abs.as_posix()}"'
    )
    html_content = html_content.replace(
        'src="logo_og.png"',
        f'src="file:///{logo_og_abs.as_posix()}"'
    )
    html_content = html_content.replace(
        'src="logo_wht.png"',
        f'src="file:///{logo_wht_abs.as_posix()}"'
    )

    # Replace relative font paths with absolute file:// URLs
    kannada_regular = PRINT_ASSETS_DIR / "NotoSansKannada-Regular.ttf"
    kannada_bold = PRINT_ASSETS_DIR / "NotoSansKannada-Bold.ttf"
    for old_font, abs_font in [
        ("url('NotoSansKannada-Regular.ttf')", f"url('file:///{kannada_regular.as_posix()}')"),
        ("url('NotoSansKannada-Bold.ttf')",    f"url('file:///{kannada_bold.as_posix()}')"),
        ("url('../NotoSansKannada-Regular.ttf')", f"url('file:///{kannada_regular.as_posix()}')"),
        ("url('../NotoSansKannada-Bold.ttf')",    f"url('file:///{kannada_bold.as_posix()}')"),
    ]:
        html_content = html_content.replace(old_font, abs_font)

    hti.screenshot(html_str=html_content, save_as=png_name)

    png_path = TEMP_DIR / png_name
    if png_path.exists():
        return png_path
    return None


def autocrop_image(img_path: Path) -> Path:
    """Auto-crop an image by trimming the background color (detected from corners)."""
    img = Image.open(img_path).convert("RGB")

    # Detect background color from top-left corner pixel
    bg_color = img.getpixel((0, 0))

    # Create a solid image of the background color, same size
    bg = Image.new("RGB", img.size, bg_color)

    # Difference between original and background
    diff = ImageChops.difference(img, bg)

    # Add a small tolerance for anti-aliased edges / compression artifacts
    # Threshold: treat pixels within ±8 of bg as background
    threshold = 10
    diff = diff.point(lambda x: 0 if x < threshold else 255)

    # Get bounding box of non-background content
    bbox = diff.getbbox()
    if bbox:
        # Add a small padding (4px) to avoid clipping edges
        pad = 4
        x1 = max(0, bbox[0] - pad)
        y1 = max(0, bbox[1] - pad)
        x2 = min(img.width, bbox[2] + pad)
        y2 = min(img.height, bbox[3] + pad)
        cropped = img.crop((x1, y1, x2, y2))
        cropped.save(str(img_path))
        print(f"   ✂ Cropped: {img.width}×{img.height} → {cropped.width}×{cropped.height}")
    else:
        print(f"   ⚠ No content detected for cropping, keeping original")

    return img_path


def png_to_tiff(png_path: Path, output_name: str):
    """Convert a PNG to TIFF at 300 DPI with LZW compression."""
    tiff_path = TIFF_OUTPUT_DIR / f"{output_name}.tiff"
    img = Image.open(png_path)

    # Convert to RGB if RGBA
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    img.save(
        str(tiff_path),
        format="TIFF",
        dpi=(DPI, DPI),
        compression="tiff_lzw",
    )
    return tiff_path


def convert_full_page(html_file: str):
    """Convert a full HTML page → PNG → TIFF."""
    name = html_file.replace("/", "_").replace("\\", "_").replace(".html", "")
    size = PAGE_SIZES.get(html_file, (1400, 2000))

    print(f"\n📄 Processing: {html_file}")
    print(f"   Screenshot size: {size[0]}×{size[1]}px")

    png_path = html_to_png(html_file, name, size)
    if png_path:
        # Auto-crop to remove background padding
        autocrop_image(png_path)

        tiff_path = png_to_tiff(png_path, name)
        # Also copy cropped PNG to output directory
        png_output = TIFF_OUTPUT_DIR / f"{name}.png"
        shutil.copy2(str(png_path), str(png_output))
        print(f"   ✅ → {tiff_path.name} + {png_output.name}")
        return tiff_path
    else:
        print(f"   ❌ Failed to generate PNG")
        return None


def cleanup():
    """Remove temp directory."""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)


def main():
    print("=" * 60)
    print("  HANS OptiCore – HTML → TIFF Converter")
    print("=" * 60)

    ensure_dirs()

    # Get unique HTML files
    html_files = list(dict.fromkeys(
        entry[0] for entry in CAPTURE_MAP
    ))

    results = []
    for html_file in html_files:
        result = convert_full_page(html_file)
        if result:
            results.append(result)

    print("\n" + "=" * 60)
    print(f"  Done! {len(results)} TIFF files generated.")
    print(f"  Output: {TIFF_OUTPUT_DIR}")
    print("=" * 60)

    # List generated files
    if results:
        print("\nGenerated files:")
        for r in results:
            size_kb = r.stat().st_size / 1024
            print(f"  • {r.name}  ({size_kb:.0f} KB)")

    cleanup()


if __name__ == "__main__":
    main()
