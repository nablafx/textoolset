@echo off
REM PyInstaller build command for Windows
REM Note: Windows uses the semicolon ';' as the path separator for --add-data

pyinstaller --noconsole --clean ^
  --name "TexToolkit" ^
  --distpath "build" ^
  --workpath "dist" ^
  --add-data "templates;templates" ^
  --hidden-import "jinja2.ext" ^
  main_desktop.py

