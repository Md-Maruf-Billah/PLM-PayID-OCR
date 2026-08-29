# PlayLive PayID OCR

Local macOS OCR automation for entering PlayLive PayID reference codes at
the cashier desk.

## Workflow

1. Cashier clicks the PlayLive code field.
2. Customer's PayID slip is placed under the fixed camera.
3. Cashier presses **F8**.
4. The program captures an image and runs three OCR passes: the primary
   (top) code, the secondary code lower on the slip, and the whole slip as a
   fallback.
5. A consensus algorithm resolves a single code, or rejects the scan if the
   passes disagree.
6. On success, the code is copied to the clipboard and pasted into the
   currently focused field, with a success sound. On failure, a failure
   sound plays and the cashier is asked to scan again.

**To install this on a cashier Mac:** see `docs/deployment.md` -- build a
`.pkg` once, hand it to coworkers, they double-click to install and it walks
them through calibration on first launch.

For running from source during development (useful if you're iterating on
the code, testing on your own Mac before packaging, or on Hammerspoon as an
alternative to the bundled F8 listener), see `docs/setup.md`.

## Three-pass consensus

| Primary | Secondary | Whole slip | Result |
|---|---|---|---|
| match | match | - | Accept, confidence **VERY HIGH** |
| reads | fails | confirms | Accept, confidence **HIGH** |
| fails | reads | confirms | Accept, confidence **HIGH** |
| reads | fails | fails/absent | Accept, confidence **MEDIUM** |
| reads | reads | disagree with each other | **Reject** -- scan again |
| reads | absent | disagrees | **Reject** -- scan again |

Codes must match `^[A-Z]{8}$`. The implementation lives in
`src/code_detector.py` (`resolve_code`), which is pure Python and covered by
`tests/test_code_detector.py`.

## Project layout

```
src/
  app.py               packaged menu bar app: F8 listener + first-run calibration
  main.py              single-shot scan, used by app.py and for dev/CLI testing
  camera.py            webcam capture (opens only for the duration of a scan)
  image_processor.py   ROI cropping, grayscale/threshold preprocessing
  ocr.py                pytesseract wrapper for the three passes
  code_detector.py     pattern extraction + consensus algorithm
  calibration.py        interactive ROI picker, shared by the CLI script and app.py
  hotkey.py             global F8 listener (pynput)
  paste.py             clipboard copy + Cmd+V into the focused field
  sounds.py             success/failure audio cue
  scan_logger.py        scan history logging (no images, no banking data)
  config.py             loads config/config.json + per-user local.json
  runtime_paths.py      resolves paths for source vs. packaged .app

config/config.json     camera, ROI, OCR, sound and logging defaults
scripts/                camera_test.py, calibrate_camera.py, build_app.sh, build_pkg.sh
packaging/              PyInstaller spec + .pkg postinstall script
tests/                   unit tests + an end-to-end OCR test on synthetic slips
docs/                    setup.md (dev), deployment.md (packaging/rollout), hammerspoon_init.lua
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/
```

## Privacy

OCR and image processing run entirely locally. Captured frames aren't saved
by default. Real customer slip scans must never be committed to this repo --
see `docs/setup.md` for details.
