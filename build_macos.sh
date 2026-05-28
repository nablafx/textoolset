#!/bin/bash
# PyInstaller build command for macOS
# Note: macOS uses the colon ':' as the path separator for --add-data

# Choose python executable (prefer python3)
if command -v python3 >/dev/null 2>&1; then
  PY_CMD=python3
else
  PY_CMD=python
fi

# Ensure a .icns exists by converting png to icns (moved to buildtools)
$PY_CMD buildtools/png_to_icns.py || {
  echo "Failed to generate .icns - ensure Pillow is installed and png exists"
  exit 1
}

pyinstaller --windowed --onefile --clean \
  --name "TexToolkit" \
  --distpath "build" \
  --workpath "dist" \
  --icon "assets/logo/logo.icns" \
  --add-data "templates:templates" \
  --add-data "assets:assets" \
  --hidden-import "jinja2.ext" \
  main_desktop.py
