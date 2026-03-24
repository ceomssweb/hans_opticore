"""
HANS OptiCore – Nameboard HTML → PNG + TIFF Generator
======================================================
Converts the new nameboard HTML to high-res PNG and TIFF files.
Uses html2image (Chrome/Chromium) for HTML→PNG, then Pillow for PNG→TIFF.

Usage:
    python generate_nameboard.py

Output folder: public/print-assets/nameboard-new/
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
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PRINT_ASSETS_DIR = SCRIPT_DIR / "public" / "print-assets"
NAMEBOARD_DIR = PRINT_ASSETS_DIR / "nameboard-new"
HTML_FILE = NAMEBOARD_DIR / "nameboard.html"
TEMP_DIR = SCRIPT_DIR / "_temp_nameboard"

# Board dimensions (width x height px for screenshot)
BOARD_WIDTH = 1920
BOARD_HEIGHT = 960
PAGE_WIDTH = 2000   # screenshot viewport
PAGE_HEIGHT = 1100

DPI = 300


def ensure_dirs():
    NAMEBOARD_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def html_to_png() -> Path:
    """Render nameboard HTML to PNG."""
    if not HTML_FILE.exists():
        print(f"  ERROR: {HTML_FILE} not found!")
        sys.exit(1)

    hti = Html2Image(
        output_path=str(TEMP_DIR),
        custom_flags=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--hide-scrollbars",
            f"--window-size={PAGE_WIDTH},{PAGE_HEIGHT}",
        ],
    )
    hti.size = (PAGE_WIDTH, PAGE_HEIGHT)

    # Read HTML and fix relative paths to absolute file:// URLs
    html_content = HTML_FILE.read_text(encoding="utf-8")

    public_dir = SCRIPT_DIR / "public"
    logo_og = public_dir / "logo_og.png"
    logo_wht = public_dir / "logo_wht.png"

    # Fix image paths
    html_content = html_content.replace(
        'src="../logo_og.png"',
        f'src="file:///{logo_og.as_posix()}"'
    )
    html_content = html_content.replace(
        'src="../logo_wht.png"',
        f'src="file:///{logo_wht.as_posix()}"'
    )

    # Fix font paths
    kannada_regular = PRINT_ASSETS_DIR / "NotoSansKannada-Regular.ttf"
    kannada_bold = PRINT_ASSETS_DIR / "NotoSansKannada-Bold.ttf"
    html_content = html_content.replace(
        "url('../NotoSansKannada-Regular.ttf')",
        f"url('file:///{kannada_regular.as_posix()}')"
    )
    html_content = html_content.replace(
        "url('../NotoSansKannada-Bold.ttf')",
        f"url('file:///{kannada_bold.as_posix()}')"
    )

    png_name = "nameboard.png"
    hti.screenshot(html_str=html_content, save_as=png_name)

    png_path = TEMP_DIR / png_name
    if png_path.exists():
        return png_path
    return None


def png_to_tiff(png_path: Path, output_name: str) -> Path:
    """Convert PNG to TIFF at 300 DPI with LZW compression."""
    tiff_path = NAMEBOARD_DIR / f"{output_name}.tiff"
    img = Image.open(png_path)

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


def cleanup():
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR, ignore_errors=True)


def main():
    print("=" * 60)
    print("  HANS OptiCore – Nameboard → PNG + TIFF Generator")
    print("=" * 60)

    ensure_dirs()

    print(f"\n📄 Processing: {HTML_FILE.name}")
    print(f"   Screenshot size: {PAGE_WIDTH}×{PAGE_HEIGHT}px")

    png_path = html_to_png()
    if png_path:
        # Copy PNG to output folder
        png_output = NAMEBOARD_DIR / "nameboard.png"
        shutil.copy2(str(png_path), str(png_output))
        print(f"   ✅ PNG → {png_output.name}")

        # Generate TIFF
        tiff_path = png_to_tiff(png_path, "nameboard")
        print(f"   ✅ TIFF → {tiff_path.name}")

        # Also try a higher-res version (2x)
        hires_hti = Html2Image(
            output_path=str(TEMP_DIR),
            custom_flags=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--hide-scrollbars",
                f"--window-size={PAGE_WIDTH * 2},{PAGE_HEIGHT * 2}",
                "--force-device-scale-factor=2",
            ],
        )
        hires_hti.size = (PAGE_WIDTH * 2, PAGE_HEIGHT * 2)

        html_content = HTML_FILE.read_text(encoding="utf-8")
        public_dir = SCRIPT_DIR / "public"
        logo_og = public_dir / "logo_og.png"
        logo_wht = public_dir / "logo_wht.png"
        html_content = html_content.replace(
            'src="../logo_og.png"',
            f'src="file:///{logo_og.as_posix()}"'
        )
        html_content = html_content.replace(
            'src="../logo_wht.png"',
            f'src="file:///{logo_wht.as_posix()}"'
        )
        kannada_regular = PRINT_ASSETS_DIR / "NotoSansKannada-Regular.ttf"
        kannada_bold = PRINT_ASSETS_DIR / "NotoSansKannada-Bold.ttf"
        html_content = html_content.replace(
            "url('../NotoSansKannada-Regular.ttf')",
            f"url('file:///{kannada_regular.as_posix()}')"
        )
        html_content = html_content.replace(
            "url('../NotoSansKannada-Bold.ttf')",
            f"url('file:///{kannada_bold.as_posix()}')"
        )

        hires_hti.screenshot(html_str=html_content, save_as="nameboard-hires.png")
        hires_png = TEMP_DIR / "nameboard-hires.png"
        if hires_png.exists():
            hires_png_out = NAMEBOARD_DIR / "nameboard-hires.png"
            shutil.copy2(str(hires_png), str(hires_png_out))
            tiff_hires = png_to_tiff(hires_png, "nameboard-hires")
            print(f"   ✅ Hi-Res PNG → {hires_png_out.name}")
            print(f"   ✅ Hi-Res TIFF → {tiff_hires.name}")
    else:
        print("   ❌ Failed to generate PNG")

    print("\n" + "=" * 60)
    print(f"  Output folder: {NAMEBOARD_DIR}")
    print("=" * 60)

    # List generated files
    for f in sorted(NAMEBOARD_DIR.glob("*.*")):
        if f.suffix in (".png", ".tiff"):
            size_kb = f.stat().st_size / 1024
            print(f"  • {f.name}  ({size_kb:.0f} KB)")

    cleanup()


if __name__ == "__main__":
    main()
