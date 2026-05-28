"""Convert assets/logo/logo.png to a Windows .ico file with common sizes.

This is the moved copy that resolves paths relative to the repository root.
Usage: python buildtools/png_to_ico.py
Produces: assets/logo/logo.ico
"""
from pathlib import Path

try:
    from PIL import Image
except Exception as e:
    raise SystemExit("Pillow is required. Install it with `pip install pillow`")

# repo root (parent of the folder containing this script)
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "assets" / "logo" / "logo.png"
DST = REPO_ROOT / "assets" / "logo" / "logo.ico"

# Compatibility for Pillow resampling constant
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = getattr(Image, "LANCZOS", getattr(Image, "BICUBIC", 1))

SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

if not SRC.exists():
    raise SystemExit(f"Source PNG not found: {SRC}")

print(f"Opening {SRC}...")
img = Image.open(SRC).convert("RGBA")

# Pillow can save ICO with multiple sizes by providing a list of resized images
icons = [img.resize(sz, RESAMPLE) for sz in SIZES]

print(f"Saving ICO to {DST} with sizes: {', '.join(str(s[0]) for s in SIZES)}")
# Save using the largest image and the sizes argument
icons[0].save(DST, format='ICO', sizes=SIZES)

print("Done.")
