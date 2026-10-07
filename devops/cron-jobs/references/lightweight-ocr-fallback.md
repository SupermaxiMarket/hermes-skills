# Lightweight OCR Fallback (tesseract)

When your model lacks vision capabilities and you need text from image-based PDFs or screenshots, use this tesseract-based fallback. No PyTorch needed — works with ~5MB of tesseract-ocr packages.

## When to use

- Model can't process images (no vision endpoint)
- PDF has no extractable text (image-based)
- Screenshot needs reading
- pymupdf returned empty text
- Can't or won't install marker-pdf (3-5GB)

## Prerequisites

```bash
apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng -y
pip install pymupdf
```

## Pattern A: Image-based PDF

### Step 1 — Check if PDF has text

```python
import pymupdf  # or import fitz
doc = pymupdf.open('document.pdf')
for page in doc:
    text = page.get_text()
    if text.strip():
        print(f"Text: {text[:500]}")
    else:
        print("No text — need OCR")
```

### Step 2a — Extract embedded images and OCR each

```python
import pymupdf
doc = pymupdf.open('document.pdf')
page = doc[0]
imgs = page.get_images(full=True)
for j, img in enumerate(imgs):
    xref = img[0]
    image_bytes = doc.extract_image(xref)['image']
    ext = doc.extract_image(xref)['ext']
    with open(f'page_img_{j+1}.{ext}', 'wb') as f:
        f.write(image_bytes)
```

Then in terminal:

```bash
tesseract page_img_1.jpeg - -l fra+eng --psm 4 2>/dev/null
```

### Step 2b — Render full page at high DPI and OCR

For PDFs where images aren't extractable individually:

```python
import pymupdf
doc = pymupdf.open('document.pdf')
page = doc[0]
mat = pymupdf.Matrix(3.0, 3.0)  # ~3x = 200+ DPI
pix = page.get_pixmap(matrix=mat)
pix.save('page_full.png')
```

```bash
tesseract page_full.png - -l fra+eng --psm 4 2>/dev/null
```

## Pattern B: Screenshot image (no vision model)

```bash
tesseract screenshot.jpg - -l fra+eng --psm 4 2>/dev/null
```

## Tesseract CLI flags

| Flag | Effect |
|------|--------|
| `-l fra+eng` | Languages (French + English) |
| `--psm 4` | Assume single column of text |
| `--psm 6` | Assume uniform block of text |
| `--psm 3` | Fully automatic (default) |
| `-` | Output to stdout |
| `2>/dev/null` | Suppress tesseract chatter |

## Limitations

- Struggles with multi-column layouts
- Handwriting is unreliable
- Small fonts (<10pt) degrade quality
- Non-Latin scripts need additional language packs (`tesseract-ocr-chi-sim`, etc.)
- No table structure preservation (just raw text)

For complex layouts, tables, or equations → install marker-pdf (~3-5GB).