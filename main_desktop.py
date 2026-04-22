import webview
import threading
from app import app


class ProApi:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def save_bib_file(self, content):
        """Uses pywebview's native thread-safe dialog."""
        if not self._window:
            return False

        # Open the native save dialog
        # This returns a tuple of file paths or None
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory='',
            save_filename='cleaned_references.bib',
            file_types=('BibTeX files (*.bib)', 'All files (*.*)')
        )

        if result:
            # result is a tuple, e.g., ('C:/path/to/file.bib',)
            file_path = result[0] if isinstance(result, tuple) else result
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                print(f"Error writing file: {e}")
                return False
        return False


def run_flask():
    # Running flask with debug=False for desktop stability
    app.run(port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    api = ProApi()

    window = webview.create_window(
        'TeX Toolset Desktop',
        'http://127.0.0.1:5000',
        js_api=api,
        width=1200,
        height=800
    )

    # Crucial: Give the API a reference to the window object
    api.set_window(window)

    webview.start()