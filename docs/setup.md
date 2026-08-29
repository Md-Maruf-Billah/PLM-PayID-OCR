# Dev setup (macOS): running from source

This is for iterating on the code or testing on your own Mac before
packaging. For installing the finished app on cashier machines, use
`docs/deployment.md` instead -- it builds a `.pkg` that bundles everything
(including Tesseract) and doesn't need any of the steps below repeated per
machine.

## 1. Prerequisites

```bash
brew install tesseract
```

## 2. Project environment

```bash
git clone git@github.com:Md-Maruf-Billah/PLM-PayID-OCR.git
cd PLM-PayID-OCR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure the camera and ROIs

1. Mount the webcam ~25-40cm above the desk, pointing straight down at a
   marked "place slip here" spot.
2. Run `python scripts/camera_test.py` to confirm the camera opens and check
   `captures/preview.jpg` for framing.
3. Run `python scripts/calibrate_camera.py`, drag a box over the primary code
   and then the secondary code. It saves the result to
   `~/Library/Application Support/PlayLive PayID Scanner/local.json`
   (overrides `config/config.json` without touching the tracked defaults).

## 4. Run a scan manually

```bash
python src/main.py
```

Click into any text field first, then run this -- it captures, OCRs,
resolves a code, and pastes it, printing the result either way.

## 5. Bind a hotkey (optional, for a source-run F8)

The packaged app (`docs/deployment.md`) has its own built-in F8 listener, so
this step is only useful if you want F8 while running from source instead
of `python src/main.py` manually. Two options:

**Hammerspoon** (a separate menu bar tool):
```bash
brew install --cask hammerspoon
```
Copy `docs/hammerspoon_init.lua` into `~/.hammerspoon/init.lua` (or
`require` it from there), updating `PYTHON_PATH` and `SCRIPT_PATH` to the
absolute paths on this Mac (the venv's `python`, and `src/main.py`). Reload
Hammerspoon's config (menu bar icon -> Reload Config).

**Or run `src/app.py` directly** (needs `pip install -r requirements-app.txt`
first) -- same F8 listener the packaged app uses, just not bundled into a
`.app` yet:
```bash
pip install -r requirements-app.txt
python src/app.py
```

## 6. macOS permissions

Under System Settings -> Privacy & Security, grant:

- **Camera** -- to Terminal/Python, so it can read the webcam.
- **Accessibility** -- to Hammerspoon (or Terminal/Python if running
  `app.py` directly), so it can send Cmd+V and listen for F8.
- **Automation** -- approve any prompt about controlling System Events.

## 7. Try it

1. Click into the PlayLive code field.
2. Place a test slip under the camera.
3. Press F8 (or run `python src/main.py` if you skipped step 5).
4. The resolved code should appear in the field; a success/failure sound
   plays depending on the consensus result (see `README.md` for how that's
   decided).

## Privacy

- OCR and all image processing run entirely locally -- nothing is uploaded.
- Captured frames are not written to disk by default; `scripts/camera_test.py`
  is the only place that saves a preview image, and `captures/`/`*.jpg`/
  `*.png` are gitignored.
- Scan logs (resolved code + outcome only, never images) go to
  `~/Library/Application Support/PlayLive PayID Scanner/logs/` -- see
  `config/config.json` -> `logging.mask_codes` to mask codes in the log.
- Never commit real customer slip scans to the repo; use synthetic/test
  codes (see `tests/test_ocr_pipeline.py` for how test slips are generated).
