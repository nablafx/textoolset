@echo off
REM PyInstaller build command for Windows
REM Note: Windows uses the semicolon ';' as the path separator for --add-data

REM Ensure an .ico exists by converting png to ico (moved to buildtools)
python buildtools\png_to_ico.py || (
  echo Failed to generate .ico - ensure Pillow is installed and png exists
  exit /b 1
)

REM Use the generated icon and include assets and templates
pyinstaller --windowed --onefile --clean ^
  --name "TexToolkit" ^
  --distpath "build" ^
  --workpath "dist" ^
  --icon "assets\\logo\\logo.ico" ^
  --add-data "templates;templates" ^
  --add-data "assets;assets" ^
  --hidden-import "jinja2.ext" ^
  main_desktop.py
