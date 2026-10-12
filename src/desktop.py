"""Desktop entry point: native window, images are read straight from disk (no upload)."""
import json
import os

import webview

from detector import STATIC_DIR, file_id, get_model, process_image

IMAGE_EXTS = (".jpg", ".jpeg", ".png")


class Api:
    def __init__(self):
        self.window = None

    def pick_files(self):
        kind = webview.FileDialog.OPEN if hasattr(webview, "FileDialog") else webview.OPEN_DIALOG
        paths = self.window.create_file_dialog(
            kind, allow_multiple=True, file_types=("Images (*.jpg;*.jpeg;*.png)",)
        )
        return list(paths or [])

    def analyze(self, path, seen):
        """Read one image from disk. `seen` holds ids already analyzed, so duplicates are skipped."""
        name = os.path.basename(path)
        try:
            with open(path, "rb") as f:
                img_bytes = f.read()
            fid = file_id(img_bytes)
            if fid in seen:
                return {"duplicate": True}
            return {"id": fid, "filename": name, **process_image(img_bytes)}
        except Exception:
            return {"error": True, "filename": name}

    def save_file(self, text, default_name):
        kind = webview.FileDialog.SAVE if hasattr(webview, "FileDialog") else webview.SAVE_DIALOG
        dest = self.window.create_file_dialog(kind, save_filename=default_name)
        if not dest:
            return False
        dest = dest if isinstance(dest, str) else dest[0]
        with open(dest, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return True


def on_drop(event, window):
    files = event.get("dataTransfer", {}).get("files", [])
    paths = [f["pywebviewFullPath"] for f in files if f.get("pywebviewFullPath")]
    paths = [p for p in paths if p.lower().endswith(IMAGE_EXTS)]
    if paths:
        window.evaluate_js(f"handlePaths({json.dumps(paths)})")


def main():
    api = Api()
    window = webview.create_window(
        "Grand Haven Parks Oak-Wilt Detector",
        os.path.join(STATIC_DIR, "index.html"),
        js_api=api,
        width=1280,
        height=860,
    )
    api.window = window

    def start():
        get_model()  # load the model up front so the first analysis isn't slow
        try:
            from webview.dom import DOMEventHandler
            window.dom.document.events.drop += DOMEventHandler(
                lambda e: on_drop(e, window), True, True
            )
        except Exception:
            pass  # drag-and-drop paths unavailable; Browse still works

    webview.start(start)


if __name__ == "__main__":
    main()
