# HANS OptiCore – Print Assets

## Files Included

| File | Description | Print Size |
|------|-------------|------------|
| `visiting-card.html` | Visiting card – Front (Founder + Partner) & Back | 3.5" × 2" (89mm × 51mm) |
| `letterhead.html` | Company letterhead template | A4 (210mm × 297mm) |
| `banner.html` | Roll-up standee, horizontal banner, table-top banner | Various sizes |

## How to View

Open any `.html` file directly in a web browser (Chrome recommended).

## How to Export to TIFF (Print-Ready)

### Option 1: Using Chrome DevTools (Quick)
1. Open the HTML file in **Google Chrome**
2. Press `Ctrl + P` (Print)
3. Set **Destination** → "Save as PDF"
4. Set **Layout** → Match the design orientation
5. Set **Margins** → None
6. Check **Background graphics** box
7. Save as PDF, then convert PDF → TIFF using any tool below

### Option 2: Screenshot at High Resolution
1. Open the HTML file in Chrome
2. Press `F12` → Console tab
3. Type: `document.body.style.zoom = '3'` (for 300 DPI equivalent)
4. Use **Snipping Tool** or `Win + Shift + S` to capture the design
5. Save as PNG, then convert to TIFF

### Option 3: Using GIMP (Free – Best for TIFF)
1. Export as PDF first (Option 1)
2. Open PDF in **GIMP** (File → Open)
3. Set resolution to **300 DPI** when importing
4. File → Export As → Choose **TIFF** format
5. Select **LZW compression** for smaller file size

### Option 4: Using ImageMagick (Command Line)
```bash
# Install ImageMagick first
# Convert PDF to 300 DPI TIFF
magick convert -density 300 visiting-card.pdf -compress lzw visiting-card.tiff
```

### Option 5: Online Converters
- [CloudConvert](https://cloudconvert.com/pdf-to-tiff)
- [Zamzar](https://www.zamzar.com/convert/pdf-to-tiff/)

## Color Profile

All designs use the HANS OptiCore brand colors:
- **Primary Navy:** #0A2540 / #0F3460
- **Accent Teal:** #0D9488 / #14B8A6
- **CTA Orange:** #F97316 / #EA580C
- **Text Dark:** #1F2937
- **Text Light:** #4B5563

For CMYK printing, convert using these approximate values:
- Navy: C:90 M:70 Y:30 K:60
- Teal: C:75 M:0 Y:40 K:0
- Orange: C:0 M:65 Y:95 K:0

## Fonts
- **Outfit** – Headings & brand name
- **DM Sans** – Body text

Both fonts are loaded from Google Fonts. For offline printing, download from:
- https://fonts.google.com/specimen/Outfit
- https://fonts.google.com/specimen/DM+Sans
