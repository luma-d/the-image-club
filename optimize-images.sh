#!/usr/bin/env bash
# Web-optimize workshop photos for the carousel.
# 1. Drop original photos into assets/gallery/originals/ (any names, jpg/png/webp)
# 2. Run this script
# It writes web-friendly progressive JPEGs to assets/gallery/NN.jpg (NN = 01..12
# in filename order), max 1600px on the long edge, quality 82 — typically
# ~200-400 KB each from a 2-3 MB WhatsApp original. EXIF rotation is applied.
set -euo pipefail
cd "$(dirname "$0")/assets/gallery"
mkdir -p originals
python3 - <<'EOF'
from PIL import Image, ImageOps
import glob, os, re

srcs = sorted(glob.glob("originals/*"), key=lambda p: os.path.basename(p).lower())
srcs = [s for s in srcs if os.path.splitext(s)[1].lower() in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")]
if not srcs:
    raise SystemExit("No images in assets/gallery/originals/ — drop the photos there first.")
for n, src in enumerate(srcs, 1):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)
    out = f"{n:02d}.jpg"
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    print(f"{out}  {im.size[0]}x{im.size[1]}  {os.path.getsize(out)//1024} KB  <- {os.path.basename(src)}")
print(f"{len(srcs)} images written to assets/gallery/ — the carousel reads 01.jpg..{len(srcs):02d}.jpg in filename order.")
EOF
