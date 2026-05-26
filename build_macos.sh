#!/bin/bash
# PyInstaller build command for macOS
# Note: macOS uses the colon ':' as the path separator for --add-data

pyinstaller --noconsole --clean \
  --name "TeXToolset" \
  --distpath "build" \
  --add-data "templates:templates" \
  --hidden-import "jinja2.ext" \
  main_desktop.py

