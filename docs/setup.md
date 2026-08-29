# Setup (macOS)

## 1. Prerequisites

```bash
brew install tesseract
brew install --cask hammerspoon
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
   and then the secondary code. It prints a JSON snippet -- save it as
   `config/local.json` (gitignored, overrides `config/config.json`).

## 4. Bind the F8 hotkey

1. Copy `docs/hammerspoon_init.lua` into `~/.hammerspoon/init.lua` (or
   `require` it from there), updating `PYTHON_PATH` and `SCRIPT_PATH` to the
   absolute paths on this Mac (the venv's `python`, and `src/main.py`).
2. Reload Hammerspoon's config (menu bar icon -> Reload Config).

## 5. macOS permissions

Under System Settings -> Privacy & Security, grant:

- **Camera** -- to Terminal/Python (or the packaged app once bundled with
  PyInstaller), so it can read the webcam.
- **Accessibility** -- to Hammerspoon (and Terminal/Python if prompted), so
  it can send Cmd+V.
- **Automation** -- approve any prompt about controlling System Events.

## 6. Try it

1. Click into the PlayLive code field.
2. Place a test slip under the camera.
3. Press F8.
4. The resolved code should appear in the field; a success/failure sound
   plays depending on the consensus result (see `README.md` for how that's
   decided).

## Privacy

- OCR and all image processing run entirely locally -- nothing is uploaded.
- Captured frames are not written to disk by default; `scripts/camera_test.py`
  and `scripts/calibrate_camera.py` are the only places that save a preview
  image, and `captures/`/`*.jpg`/`*.png` are gitignored.
- `logs/scan_history.log` records only the resolved code and outcome (see
  `config/config.json` -> `logging.mask_codes` to mask codes in the log).
- Never commit real customer slip scans to the repo; use synthetic/test
  codes (see `tests/test_ocr_pipeline.py` for how test slips are generated).
