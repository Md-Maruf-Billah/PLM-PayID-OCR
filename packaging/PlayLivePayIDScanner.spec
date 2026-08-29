# PyInstaller spec for the packaged menu bar app.
#
# Build via scripts/build_app.sh, which resolves the Homebrew-installed
# tesseract binary/tessdata and passes their paths in through the
# TESSERACT_BIN / TESSDATA_DIR environment variables read below -- do not
# invoke `pyinstaller` on this file directly without setting those first.

import os

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))  # noqa: F821 (SPECPATH is injected by PyInstaller)
SRC = os.path.join(ROOT, "src")

tesseract_bin = os.environ["TESSERACT_BIN"]
tessdata_dir = os.environ["TESSDATA_DIR"]

block_cipher = None

a = Analysis(  # noqa: F821
    [os.path.join(SRC, "app.py")],
    pathex=[SRC],
    binaries=[(tesseract_bin, "tesseract-bin")],
    datas=[
        (tessdata_dir, "tessdata"),
        (os.path.join(ROOT, "config", "config.json"), "config"),
        (os.path.join(ROOT, "assets"), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PlayLive PayID Scanner",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="PlayLive PayID Scanner",
)

app = BUNDLE(  # noqa: F821
    coll,
    name="PlayLive PayID Scanner.app",
    icon=None,
    bundle_identifier="com.playlive.payidscanner",
    info_plist={
        "LSUIElement": True,
        "NSCameraUsageDescription": "Scans PayID slips placed under the camera.",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
    },
)
