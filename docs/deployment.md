# Deployment: build once, install on every cashier Mac

This turns the project into `PlayLive PayID Scanner.app` -- a menu bar app
that listens for **F8** globally (no Hammerspoon needed), bundles Tesseract
so coworkers don't need Homebrew, and walks them through camera calibration
the first time it opens. It ships as a `.pkg` installer: double-click,
click through, done.

## 1. Build it (once)

Both scripts must run on macOS -- PyInstaller can't cross-build a `.app`
from Linux or Windows. Two ways to get that macOS build environment:

**Option A -- GitHub Actions (no Mac needed, free):** the repo includes
`.github/workflows/build-app.yml`, which builds on GitHub's free hosted
macOS runners.
1. On GitHub, open the repo -> **Actions** tab -> **Build macOS app** (left
   sidebar) -> **Run workflow** button -> **Run workflow**.
2. Wait for it to finish (a few minutes) -- it builds two versions, one for
   Apple Silicon Macs and one for Intel Macs.
3. Click into the finished run, scroll to **Artifacts**, and download
   `PlayLive-PayID-Scanner-apple-silicon` or `PlayLive-PayID-Scanner-intel`
   (whichever matches the cashier Mac -- not sure which? run `uname -m` in
   Terminal on that Mac: `arm64` = Apple Silicon, `x86_64` = Intel; if in
   doubt, download both and try the matching one). Each download is a
   `.zip` containing the `.pkg` installer.

This runs entirely on GitHub's infrastructure and costs nothing on the free
tier (a build takes a few minutes, well under the free monthly minutes).

**Option B -- on your own Mac:**
```bash
./scripts/build_app.sh
./scripts/build_pkg.sh
```
Needs Xcode Command Line Tools + Homebrew set up locally first (see
`docs/setup.md`).

Either way you end up with `PlayLive PayID Scanner Installer.pkg` -- that
single file is what you hand to coworkers (AirDrop, USB stick, shared drive
-- whatever is easiest).

## 2. Install on a coworker's Mac

1. Copy `PlayLive PayID Scanner Installer.pkg` onto their Mac.
2. Double-click it.
3. **This package is unsigned** (no Apple Developer ID / notarization), so
   Gatekeeper will block it the first time with something like *"Apple
   could not verify... malware"* or *"unidentified developer"*. To get past
   it once: **Control-click the .pkg -> Open -> Open**, or go to
   **System Settings -> Privacy & Security**, scroll down, and click
   **Open Anyway** next to the blocked-app notice, then try opening it
   again. This is only needed once per Mac, for the installer itself.
4. Follow the installer -- it installs the app to `/Applications` and sets
   it to start automatically at login.
5. Open **PlayLive PayID Scanner** from Applications the first time (after
   that, it starts on its own at login).

## 3. First launch on their machine

- macOS will prompt for **Camera** access -- allow it.
- macOS will prompt for **Accessibility** access (needed for the F8 global
  hotkey and pasting) -- allow it in System Settings if it isn't prompted
  automatically.
- A dialog walks them through calibration: place a test slip under the
  camera, then drag a box over the primary code and the secondary code.
  This is saved per-machine, so it only needs to happen once per station
  (or again later if the camera gets moved/replaced -- see below).
- After that, the app sits in the menu bar. F8 is live from any app: click
  into the PlayLive code field, place a slip, press F8.

Once it's working, print `docs/cashier-quick-start.md` and leave it at the
register -- it's the one-page version of steps 4 onward, written for the
cashier rather than for you.

## 4. Recalibrating later

If the camera gets bumped, replaced, or moved to a new desk position, click
the menu bar icon -> **Recalibrate**, and repeat the drag-a-box steps.

## 5. Where things live on each machine

- App: `/Applications/PlayLive PayID Scanner.app`
- Calibration + scan logs: `~/Library/Application Support/PlayLive PayID Scanner/`
- Auto-start: `/Library/LaunchAgents/com.playlive.payidscanner.plist`

## 6. Updating to a new version

Bump the version in the `VERSION` file, rebuild both scripts, and re-share
the new `.pkg`. Reinstalling over an existing install just replaces the
`.app` in place -- calibration and logs (which live outside
`/Applications`) are untouched.

After installing an update, quit the app from the menu bar and reopen it
(or just restart the Mac) so it picks up the new build -- the LaunchAgent
doesn't restart an already-running instance on its own.

## 7. Uninstalling

```bash
launchctl bootout gui/$(id -u) /Library/LaunchAgents/com.playlive.payidscanner.plist
sudo rm /Library/LaunchAgents/com.playlive.payidscanner.plist
rm -rf "/Applications/PlayLive PayID Scanner.app"
rm -rf ~/Library/Application\ Support/PlayLive\ PayID\ Scanner
```

## Why unsigned, and should you fix that?

Signing + notarizing (so Gatekeeper never complains) requires an Apple
Developer Program membership ($99/year) and running `xcrun notarytool`
from a Mac with Xcode's command line tools during the build. For an
internal tool used on a handful of machines you control, the one-time
Control-click bypass per Mac is a reasonable tradeoff. If this ends up
going to many more machines, or Gatekeeper's warning message becomes a
support burden, that's worth revisiting -- ask and it can be added to the
build script.
