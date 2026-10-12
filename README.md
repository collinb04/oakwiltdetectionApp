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

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/desktop.py
```

Click **Browse files** or drag JPG/PNG images onto the window (max 75). Duplicate photos are skipped by content. Filter results, mark predictions Good/Bad, and export CSV or GeoJSON with a native Save dialog.

## Package for users

```bash
pip install pyinstaller
pyinstaller --windowed --add-data "src/oak_wilt_3.h5:src" --add-data "src/static:src/static" --paths src src/desktop.py
```

On Windows use `;` instead of `:` in `--add-data`.

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
