# Grand Haven Parks Oak-Wilt Detector

A local desktop app that classifies oak tree photos into four oak wilt categories using a TensorFlow model. It reads images straight from disk (nothing is uploaded), extracts GPS data from EXIF, and exports CSV/GeoJSON for detected cases.

## Classification

| Category | Confidence |
| --- | --- |
| THIS PICTURE HAS OAK WILT | >99.5% |
| HIGH CHANCE OF OAK WILT | 90–99.5% |
| CHANGES OF COLORS ON TREE LEAVES | 70–90% |
| Not an Oak Wilt | ≤70% |

## Run

Requires Python 3.9, 3.10, or 3.11 (the pinned TensorFlow has no builds for newer versions).

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/desktop.py
```

Click **Browse files** or drag JPG/PNG images onto the window (max 75). Duplicate photos are skipped by content. Filter results, mark predictions Good/Bad, and export CSV or GeoJSON with a native Save dialog.

## Package for users

The app is packaged with [PyInstaller](https://pyinstaller.org) using `OakWiltDetector.spec`, which bundles the model, the UI, and all of TensorFlow. The same spec file works on both platforms, but PyInstaller cannot cross-compile: build the Mac app on a Mac and the Windows app on Windows.

### Before building (both platforms)

1. The model is stored with Git LFS. Make sure the real file is present, not a pointer (it should be many MB, not a few hundred bytes):

   ```bash
   git lfs install
   git lfs pull
   ```

2. Set up the virtual environment as in [Run](#run), then install PyInstaller into it:

   ```bash
   pip install pyinstaller
   ```

3. Confirm `python src/desktop.py` works before packaging.

### macOS

```bash
source venv/bin/activate
pyinstaller --noconfirm --clean OakWiltDetector.spec
```

Output: `dist/OakWiltDetector.app`. Double-click it to test.

To share it, zip the app with `ditto` (a plain `zip` can break the bundle):

```bash
ditto -c -k --keepParent dist/OakWiltDetector.app OakWiltDetector-mac.zip
```

Notes:

* The app is built for the architecture of the Mac it was built on. An Apple Silicon build does not run on Intel Macs, so build on each if you need both.
* The app is not signed or notarized, so macOS blocks it on first launch. Users have to right-click the app and choose **Open**, or allow it under **System Settings → Privacy & Security → Open Anyway**. On recent macOS versions only the System Settings route works.

### Windows

In PowerShell or Command Prompt:

```bat
venv\Scripts\activate
pyinstaller --noconfirm --clean OakWiltDetector.spec
```

Output: the folder `dist\OakWiltDetector\`, containing `OakWiltDetector.exe` and an `_internal` folder. The exe needs the files next to it, so always ship the whole folder.

To share it, zip the folder:

```powershell
Compress-Archive -Path dist\OakWiltDetector -DestinationPath OakWiltDetector-windows.zip
```

Users unzip it and run `OakWiltDetector.exe`.

Notes:

* The window uses the Microsoft Edge WebView2 runtime. It is preinstalled on Windows 11 and most up-to-date Windows 10 machines; otherwise install it from Microsoft.
* The exe is not signed, so SmartScreen shows "Windows protected your PC". Users click **More info → Run anyway**.

### Troubleshooting

* **Model fails to load in the packaged app:** `src/oak_wilt_3.h5` was an LFS pointer at build time. Run `git lfs pull` and rebuild.
* **App closes immediately with no message:** set `console=True` in `OakWiltDetector.spec`, rebuild, and run the executable from a terminal to see the error.
* **Stale build:** delete `build/` and `dist/` and rebuild.

The package is large (several hundred MB) because it includes TensorFlow, and the first launch takes a few seconds while the model loads.

## Files

```
src/
├── desktop.py       # window, file picker, save dialog
├── detector.py      # model loading, classification, EXIF GPS
├── static/index.html  # UI
└── oak_wilt_3.h5    # TensorFlow model
```

## Limitations

* Only images with GPS EXIF data appear in the GeoJSON.
* Predictions are probabilistic and should be verified by a person.
