"""Generate a macOS .icns file from assets/logo/logo.png.

This is the moved copy that resolves paths relative to the repository root.
Usage: python buildtools/png_to_icns.py
Produces: assets/logo/logo.icns
"""
from pathlib import Path
import shutil
import subprocess
import sys

try:
    from PIL import Image
except Exception:
    raise SystemExit("Pillow is required. Install it with `pip install pillow`")

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "assets" / "logo" / "logo.png"
ICONSET_DIR = REPO_ROOT / "assets" / "logo" / "logo.iconset"
DST_ICNS = REPO_ROOT / "assets" / "logo" / "logo.icns"

# Compatibility for Pillow resampling constant
try:
    RESAMPLE = Image.Resampling.LANCZOS
except Exception:
    RESAMPLE = getattr(Image, "LANCZOS", getattr(Image, "BICUBIC", 1))

if not SRC.exists():
    raise SystemExit(f"Source PNG not found: {SRC}")

# Iconset mapping: filenames -> pixel sizes
icon_specs = {
    "icon_16x16.png": (16, 16),
    "icon_16x16@2x.png": (32, 32),
    "icon_32x32.png": (32, 32),
    "icon_32x32@2x.png": (64, 64),
    "icon_128x128.png": (128, 128),
    "icon_128x128@2x.png": (256, 256),
    "icon_256x256.png": (256, 256),
    "icon_256x256@2x.png": (512, 512),
    "icon_512x512.png": (512, 512),
    "icon_512x512@2x.png": (1024, 1024),
}

print(f"Opening source image: {SRC}")
img = Image.open(SRC).convert("RGBA")

# Ensure iconset directory is clean
if ICONSET_DIR.exists():
    shutil.rmtree(ICONSET_DIR)
ICONSET_DIR.mkdir(parents=True, exist_ok=True)

print(f"Creating iconset in {ICONSET_DIR}...")
for name, (w, h) in icon_specs.items():
    out_path = ICONSET_DIR / name
    resized = img.resize((w, h), RESAMPLE)
    resized.save(out_path, format="PNG")

# Try to use iconutil if available (macOS)
print("Attempting to run iconutil to create .icns (macOS)...")
try:
    subprocess.check_call(["iconutil", "-c", "icns", "-o", str(DST_ICNS), str(ICONSET_DIR)])
    print(f"Created {DST_ICNS}")
    # clean up iconset directory
    shutil.rmtree(ICONSET_DIR)
    sys.exit(0)
except FileNotFoundError:
    # iconutil not present on this system (not macOS or not installed)
    print("iconutil not found on PATH; falling back to Pillow ICNS save (single-size)")
except subprocess.CalledProcessError as e:
    print("iconutil failed:", e)
    print("Falling back to Pillow ICNS save (single-size)")

# Fallback: try saving ICNS directly with Pillow (may be single size)
try:
    largest = max(spec[0] for spec in icon_specs.values())
    icns_img = img.resize((largest, largest), RESAMPLE)
    icns_img.save(DST_ICNS, format="ICNS")
    print(f"Saved ICNS via Pillow to {DST_ICNS}")
    if ICONSET_DIR.exists():
        shutil.rmtree(ICONSET_DIR)
    sys.exit(0)
except Exception as e:
    print("Failed to create ICNS:", e)
    sys.exit(1)
