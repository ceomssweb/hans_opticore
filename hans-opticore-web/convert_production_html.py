"""
HANS OptiCore – Production HTML to PNG/TIFF Converter
======================================================
Converts all HTML files in Production/Raw-html/ folder to high-resolution images.
- All HTML files → High-quality PNG (stored in Production/PNG/)
- name-board.html → TIFF for print (stored in Production/Print/)

Uses html2image (Chrome/Chromium) for HTML→PNG, then Pillow for PNG→TIFF.

Usage:
    python convert_production_html.py

Requirements:
    pip install html2image pillow
"""

import os
import sys
import shutil
from pathlib import Path

try:
    from html2image import Html2Image
except ImportError:
    print("ERROR: html2image not installed. Run: pip install html2image")
    sys.exit(1)

try:
    from PIL import Image, ImageChops
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


# ── Paths ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PRODUCTION_DIR = SCRIPT_DIR / "Production"
RAW_HTML_DIR = PRODUCTION_DIR / "Raw-html"
PNG_OUTPUT_DIR = PRODUCTION_DIR / "PNG"
TIFF_OUTPUT_DIR = PRODUCTION_DIR / "Print"
TEMP_DIR = SCRIPT_DIR / "_temp_production"

# DPI for TIFF output
DPI = 300

# ── HTML Files and their capture dimensions ──────────────────
# Format: (html_relative_path, output_name, width, height, page_width, page_height)
# page_width/height is the viewport size for the screenshot

CAPTURE_CONFIG = {
    # Blue themed files
    "Blue/banner 1.html": {
        "output_name": "Blue_banner-1-rollup",
        "width": 500, "height": 1500,
        "page_width": 600, "page_height": 1600
    },
    "Blue/banner 2.html": {
        "output_name": "Blue_banner-2-horizontal",
        "width": 1200, "height": 400,
        "page_width": 1400, "page_height": 600
    },
    "Blue/banner 3.html": {
        "output_name": "Blue_banner-3-tabletop",
        "width": 900, "height": 280,
        "page_width": 1100, "page_height": 500
    },
    "Blue/letterhead.html": {
        "output_name": "Blue_letterhead-A4",
        "width": 794, "height": 1123,  # A4 at 96 DPI
        "page_width": 900, "page_height": 1300
    },
    "Blue/visiting-card - 1.1.html": {
        "output_name": "Blue_visiting-card-front-1",
        "width": 1050, "height": 600,  # 3.5in x 2in at 300 DPI
        "page_width": 1200, "page_height": 800
    },
    "Blue/visiting-card - 1.2.html": {
        "output_name": "Blue_visiting-card-front-2",
        "width": 1050, "height": 600,
        "page_width": 1200, "page_height": 800
    },
    "Blue/visiting-card - back.html": {
        "output_name": "Blue_visiting-card-back",
        "width": 1050, "height": 600,
        "page_width": 1200, "page_height": 800
    },
    
    # Light themed files
    "light/banner-light 1.html": {
        "output_name": "Light_banner-1-rollup",
        "width": 500, "height": 1500,
        "page_width": 600, "page_height": 1600
    },
    "light/banner-light 2.html": {
        "output_name": "Light_banner-2-horizontal",
        "width": 1200, "height": 400,
        "page_width": 1400, "page_height": 600
    },
    "light/banner-light 3.html": {
        "output_name": "Light_banner-3-tabletop",
        "width": 900, "height": 280,
        "page_width": 1100, "page_height": 500
    },
    "light/letterhead-light.html": {
        "output_name": "Light_letterhead-A4",
        "width": 794, "height": 1123,
        "page_width": 900, "page_height": 1300
    },
    "light/visiting-card-light - 1.1.html": {
        "output_name": "Light_visiting-card-front-1",
        "width": 1050, "height": 600,
        "page_width": 1200, "page_height": 800
    },
    "light/visiting-card-light - 1.2.html": {
        "output_name": "Light_visiting-card-front-2",
        "width": 1050, "height": 600,
        "page_width": 1200, "page_height": 800
    },
    "light/visiting-card-light - back.html": {
        "output_name": "Light_visiting-card-back",
        "width": 1050, "height": 600,
        "page_width": 1200, "page_height": 800
    },
    
    # Name board (for both PNG and TIFF)
    "name-board.html": {
        "output_name": "name-board-main",
        "width": 1920, "height": 720,  # 8ft x 3ft scaled
        "page_width": 2100, "page_height": 1000,
        "tiff": True  # Generate TIFF for this one
    },
}


def ensure_dirs():
    """Create output directories."""
    PNG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TIFF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    (PNG_OUTPUT_DIR / "Blue").mkdir(parents=True, exist_ok=True)
    (PNG_OUTPUT_DIR / "Light").mkdir(parents=True, exist_ok=True)


def fix_html_paths(html_content: str, html_dir: Path) -> str:
    """Fix relative paths in HTML to use absolute file:// URLs."""
    # Fix logo paths - they are in the Raw-html folder
    logo_og = RAW_HTML_DIR / "logo_og.png"
    logo_wht = RAW_HTML_DIR / "logo_wht.png"
    logo_grey = RAW_HTML_DIR / "logo_grey.png"
    
    # Various src patterns
    replacements = [
        ('src="logo_og.png"', f'src="file:///{logo_og.as_posix()}"'),
        ('src="logo_wht.png"', f'src="file:///{logo_wht.as_posix()}"'),
        ('src="logo_grey.png"', f'src="file:///{logo_grey.as_posix()}"'),
        ('src="../logo_og.png"', f'src="file:///{logo_og.as_posix()}"'),
        ('src="../logo_wht.png"', f'src="file:///{logo_wht.as_posix()}"'),
        ('src="../logo_grey.png"', f'src="file:///{logo_grey.as_posix()}"'),
    ]
    
    for old, new in replacements:
        html_content = html_content.replace(old, new)
    
    # Fix font paths
    kannada_regular = RAW_HTML_DIR / "NotoSansKannada-Regular.ttf"
    kannada_bold = RAW_HTML_DIR / "NotoSansKannada-Bold.ttf"
    
    font_replacements = [
        ("url('NotoSansKannada-Regular.ttf')", f"url('file:///{kannada_regular.as_posix()}')"),
        ("url('NotoSansKannada-Bold.ttf')", f"url('file:///{kannada_bold.as_posix()}')"),
        ("url('../NotoSansKannada-Regular.ttf')", f"url('file:///{kannada_regular.as_posix()}')"),
        ("url('../NotoSansKannada-Bold.ttf')", f"url('file:///{kannada_bold.as_posix()}')"),
    ]
    
    for old, new in font_replacements:
        html_content = html_content.replace(old, new)
    
    return html_content


# Scale factor for high-resolution rendering (2x = crisp text, 3x = print quality)
SCALE_FACTOR = 2

def html_to_png(html_file: str, config: dict) -> Path:
    """Render an HTML file to a PNG screenshot at high resolution."""
    html_path = RAW_HTML_DIR / html_file
    if not html_path.exists():
        print(f"  WARNING: {html_file} not found, skipping...")
        return None

    page_width = config["page_width"] * SCALE_FACTOR
    page_height = config["page_height"] * SCALE_FACTOR
    output_name = config["output_name"]

    hti = Html2Image(
        output_path=str(TEMP_DIR),
        custom_flags=[
            "--no-sandbox",
            "--headless=new",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            f"--force-device-scale-factor={SCALE_FACTOR}",
            f"--window-size={page_width},{page_height}",
        ],
    )
    hti.size = (page_width, page_height)

    # Read HTML and fix paths
    html_content = html_path.read_text(encoding="utf-8")
    html_content = fix_html_paths(html_content, html_path.parent)

    png_name = f"{output_name}.png"
    hti.screenshot(html_str=html_content, save_as=png_name)

    png_path = TEMP_DIR / png_name
    if png_path.exists():
        return png_path
    return None


def autocrop_image(img_path: Path) -> Path:
    """Auto-crop an image by trimming the background color with zero padding."""
    img = Image.open(img_path).convert("RGB")

    # Detect background color from top-left corner pixel
    bg_color = img.getpixel((0, 0))
    
    # Create a solid image of the background color
    bg = Image.new("RGB", img.size, bg_color)
    
    # Difference between original and background
    diff = ImageChops.difference(img, bg)
    
    # Threshold for anti-aliased edges - tighter threshold for cleaner edges
    threshold = 5
    diff = diff.point(lambda x: 0 if x < threshold else 255)
    
    # Get bounding box
    bbox = diff.getbbox()
    if bbox:
        # No padding - crop exactly to content
        cropped = img.crop(bbox)
        cropped.save(str(img_path), quality=100)
        print(f"     Cropped: {img.width}x{img.height} -> {cropped.width}x{cropped.height}")
    
    return img_path


def png_to_tiff(png_path: Path, output_name: str) -> Path:
    """Convert a PNG to high-resolution TIFF at 300 DPI with LZW compression."""
    tiff_path = TIFF_OUTPUT_DIR / f"{output_name}.tiff"
    img = Image.open(png_path)
    
    # Convert RGBA to RGB with white background
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")
    
    # Image is already rendered at SCALE_FACTOR resolution
    # For 300 DPI print, we may need additional upscaling
    # At SCALE_FACTOR=2, we have ~192 effective DPI, scale up to 300
    target_scale = 300 / (96 * SCALE_FACTOR)
    if target_scale > 1:
        new_width = int(img.width * target_scale)
        new_height = int(img.height * target_scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    img.save(
        str(tiff_path),
        format="TIFF",
        dpi=(DPI, DPI),
        compression="tiff_lzw",
    )
    
    print(f"     TIFF: {tiff_path.name} ({img.width}x{img.height} @ {DPI} DPI)")
    return tiff_path


def process_html_file(html_file: str, config: dict) -> tuple:
    """Process a single HTML file to PNG (and optionally TIFF)."""
    output_name = config["output_name"]
    
    print(f"\n  Processing: {html_file}")
    print(f"     Output: {output_name}")
    print(f"     Size: {config['width']}x{config['height']}px")
    
    # Generate PNG
    png_path = html_to_png(html_file, config)
    
    if png_path is None:
        print(f"     FAILED to generate PNG")
        return None, None
    
    # Auto-crop
    autocrop_image(png_path)
    
    # Determine output subfolder based on filename
    if html_file.startswith("Blue/"):
        png_output = PNG_OUTPUT_DIR / "Blue" / f"{output_name}.png"
    elif html_file.startswith("light/"):
        png_output = PNG_OUTPUT_DIR / "Light" / f"{output_name}.png"
    else:
        png_output = PNG_OUTPUT_DIR / f"{output_name}.png"
    
    # Copy PNG to output
    shutil.copy2(str(png_path), str(png_output))
    print(f"     PNG saved: {png_output.relative_to(PRODUCTION_DIR)}")
    
    # Generate TIFF if configured
    tiff_path = None
    if config.get("tiff", False):
        tiff_path = png_to_tiff(png_path, output_name)
    
    return png_output, tiff_path


def cleanup():
    """Remove temp directory."""
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        print("\n  Cleaned up temporary files.")


def main():
    print("=" * 70)
    print("   HANS OptiCore – Production HTML to PNG/TIFF Converter")
    print("=" * 70)
    
    ensure_dirs()
    
    png_results = []
    tiff_results = []
    
    for html_file, config in CAPTURE_CONFIG.items():
        png_path, tiff_path = process_html_file(html_file, config)
        if png_path:
            png_results.append(png_path)
        if tiff_path:
            tiff_results.append(tiff_path)
    
    print("\n" + "=" * 70)
    print(f"   DONE!")
    print(f"   Generated {len(png_results)} PNG files in: Production/PNG/")
    print(f"   Generated {len(tiff_results)} TIFF files in: Production/Print/")
    print("=" * 70)
    
    # List generated files
    if png_results:
        print("\n  PNG Files:")
        for p in png_results:
            size_kb = p.stat().st_size / 1024
            print(f"    - {p.relative_to(PRODUCTION_DIR)}  ({size_kb:.1f} KB)")
    
    if tiff_results:
        print("\n  TIFF Files (High-Resolution Print):")
        for t in tiff_results:
            size_mb = t.stat().st_size / (1024 * 1024)
            print(f"    - {t.relative_to(PRODUCTION_DIR)}  ({size_mb:.2f} MB)")
    
    cleanup()


if __name__ == "__main__":
    main()
