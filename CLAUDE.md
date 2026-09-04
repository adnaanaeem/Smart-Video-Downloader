# Smart Video Downloader — Project Handoff

A desktop GUI (PyQt6) that wraps `yt-dlp` + `ffmpeg` to fetch and download video/audio
from hundreds of sites (YouTube, TikTok, Instagram, Facebook, Vimeo, Dailymotion, ...).
Single-window app, dark theme, download queue with progress bars, MP3 conversion,
cookies-based private video support, self-updating `yt-dlp`/`ffmpeg`/app binary.

**Maintainer:** Adnan Naeem · **Current version:** see `config.py` → `APP_VERSION`
(README.md's "What's New" section is user-facing changelog; this file's Changelog
section below is the developer/agent-facing one — keep both in sync).

> **Instruction for future Claude sessions:** whenever you fix a bug or add a
> feature in this repo, append an entry to the **Changelog** section at the
> bottom of this file (what changed, why, which file/function). This is the
> project's institutional memory — don't skip it.

---

## Tech Stack

- **Language:** Python 3
- **GUI:** PyQt6 (`QApplication`/`QMainWindow`, hand-rolled dark theme via stylesheet)
- **Downloader backend:** `yt-dlp.exe` (bundled binary, invoked via `subprocess`)
- **Audio/video muxing:** `ffmpeg.exe` (bundled binary)
- **HTTP:** `requests` (for dependency downloads, GitHub release checks, thumbnails)
- **Packaging:** PyInstaller (`Smart Video Downloader.spec`) → Inno Setup (`setup_script.iss`)
- **Threading model:** every blocking operation (fetch, download, dependency
  download, version check) runs in a `QThread` + `QObject` worker with
  `pyqtSignal`-based callbacks back to the UI thread — see `workers.py`.

(Historical note: `requirements.txt` used to list `PyQt5` despite all code
importing `PyQt6` since the v2.0 migration, and was missing `requests`/
`packaging`. Fixed 2026-09-04 — see Changelog.)

## Entry Point & Run/Build

- Run from source: `python main.py` (needs `yt-dlp`/`ffmpeg` — `.exe` suffix on
  Windows, none on macOS, see `workers.py` `EXE_SUFFIX` — in the working dir, or
  the app will prompt to auto-download them on first launch).
- **The app is cross-platform (Windows + macOS/Apple Silicon)** as of v2.1.2 —
  see the 2026-09-04 (v2.1.2) Changelog entry for the full story of what that
  required (platform-conditional binary paths/URLs/extraction,
  `CREATE_NO_WINDOW` guard, etc.). Windows remains the only platform anyone has
  actually run the source app on directly in this repo's history; macOS support
  is CI-built and CI-verified only (no Mac hardware available to the agent that
  built it) — treat mac-specific code paths with a bit more scrutiny until a
  human confirms real-machine behavior.
- Build (manual/local): `pyinstaller --name "Smart Video Downloader" --onefile
  --windowed --icon="icon.ico" --add-data "icon.ico;." --add-data "icon.png;."
  main.py` on Windows (swap `icon.ico`→`icon.icns` and `;`→`:` on macOS; see
  `.github/workflows/release.yml` for the exact mac invocation, including
  `.icns` generation via `sips`/`iconutil`). `*.spec` files are gitignored —
  regenerated per-build, never hand-maintained or committed.
- Installer: `setup_script.iss` (Inno Setup, Windows only) packages the
  PyInstaller output — paths inside it are relative to the `.iss` file's own
  location, run `ISCC.exe setup_script.iss` from the repo root. macOS packaging
  uses `hdiutil` to produce a `.dmg` directly from the PyInstaller `.app` output
  (no separate installer script).
- **CI/CD:** `.github/workflows/release.yml` builds both installers and
  publishes them to a GitHub Release on every `v*` tag push (or manual
  `workflow_dispatch`). See that file and the v2.1.2 changelog entry for the
  full pipeline shape.
- `dist/`, `build/`, `Output/` are build artifacts; `ffmpeg-master-latest-win64-gpl/`
  is a leftover extraction folder from a manual ffmpeg download.
- `Smart-Video-Downloader/` (nested dir) is an empty stray folder containing only
  a `.git` and `.gitattributes` — not part of the app, likely a leftover from an
  earlier repo init. Safe to ignore; ask before deleting.

## Code Map

| File | Responsibility |
|---|---|
| `main.py` | `SmartVideoDownloader(QMainWindow)` — the entire UI: builds all panels (`_create_*` methods), wires button clicks to worker threads, owns app state (`fetched_data`, `download_items`, `save_path`, `cookies_path`), persists settings, drives the dependency-check / self-update flows. This is the file you'll touch for almost any feature/bug work. |
| `workers.py` | All background work as `QObject` subclasses moved to `QThread`s, plus custom widgets/dialogs (`Spinner`, `ModalDialog`, `DeveloperDialog`, `DownloadItem`) and the shared `WorkerSignals` class (all cross-thread signals live here). |
| `config.py` | Static config: app title/version, developer info, dependency download URLs, GitHub API URLs for update checks. Bump `APP_VERSION` here on release. |
| `theme.py` | Single source of truth for colors (`THEME` dict) and `FONT_FAMILY`. |
| `styles.py` | `generate_stylesheet()` — builds the full Qt stylesheet string from `theme.py`, applied once via `app.setStyleSheet(...)` in `main.py`. |
| `localization.py` | `STRINGS` dict — every user-facing string. Add new UI text here, not inline, to keep the app localization-ready. |
| `config.json` | Runtime example/leftover of the settings file shape (actual settings persist to `%LocalAppData%/.../settings.json` via `get_settings_path()` in `main.py`, not this file — this one looks like a stray dev artifact). |
| `setup_script.iss` | Inno Setup installer script (Windows). |
| `.github/workflows/release.yml` | GitHub Actions: builds Windows + macOS (arm64 + Intel) installers and publishes them to a GitHub Release on tag push. |
| `.github/workflows/test.yml` | GitHub Actions: runs `tests/` on every push/PR to `main`. |
| `tests/` | Pytest suite — `conftest.py` (headless `QApplication` fixture + fixture loader), `fixtures/*.json` (hand-built `--dump-json`-shaped format lists), `test_formats_table.py` (formats-table population/filter regressions), `test_workers.py` (pure-logic checks: bin paths, `parse_flat_playlist_output`). No subprocess/network calls in any test. Run with `python -m pytest tests/ -v`. |
| `icon.ico` / `icon.png` | App icons (window icon + header logo). `icon.icns` (macOS) is generated at CI build time, not committed. |
| `yt-dlp` / `ffmpeg` (`.exe` on Windows) | Bundled binaries, gitignored — auto-downloaded by the app if missing or corrupted, platform-appropriate URL picked in `workers.py` (`YTDlpWorker`, `FFmpegDownloadWorker`). |

## Architecture / Key Flows

**Startup:** `SmartVideoDownloader.__init__` → `_setup_ui()` builds all panels
(hidden until needed) → `_load_settings()` restores `save_path`/`cookies_path`
from disk → `check_dependencies()` verifies `yt-dlp.exe`/`ffmpeg.exe` exist,
prompting a forced download (`YTDlpWorker`/`FFmpegDownloadWorker`) if not, then
silently checks for app updates (`AppUpdateCheckWorker` against `config.APP_API_URL`,
a GitHub "latest release" endpoint).

**Fetch flow:** URL entered → `_on_fetch_clicked` spins up `FetchWorker`, which
runs `yt-dlp.exe <url> --dump-json --no-playlist` and parses the JSON → on
success, `_populate_video_data()` (title/description/thumbnail) and
`_populate_formats_table()` build the formats table. Format rows are
synthesized by pairing `video_formats` (video-only) with `audio_formats`
(audio-only) per language, plus pre-merged formats and a dedicated MP3 row
(`_add_mp3_row`, disabled if `ffmpeg.exe` missing).

**Download flow:** clicking a row's Download button → `_on_download_clicked`
checks for filename collision (overwrite confirmation) → `_start_download_worker`
spins up `DownloadWorker`, which runs `yt-dlp.exe <url> -f
"<video_id>+<audio_id>" -o <path> --merge-output-format mp4` (or just
`<video_id>` for pre-merged formats), streams stdout for `[download] NN%` lines
via regex to update the per-item progress bar. MP3 downloads go through the
separate `Mp3DownloadWorker` (`-x --audio-format mp3`) with its own progress regex.
Every queued download gets a `DownloadItem` widget appended to
`queue_list_layout`, keyed by a `unique_id` string.

**Error handling:** `handle_fetch_error` / `_on_download_finished` sniff the
error text for private-video keywords ("private", "login required", "members
only", "sign in", ...) and route to `_show_private_video_help()` with
cookies-file instructions; other errors go to `_show_error()`, which collapses
long messages behind a "Details" button (scrollable `ModalDialog`).

**Self-update flows:** `_on_ytdlp_update_clicked` → `VersionCheckWorker` compares
local `yt-dlp.exe --version` vs `config.YT_DLP_API_URL` latest tag → on accept,
re-downloads via `YTDlpWorker` with `is_updating_ytdlp=True` so
`_on_ytdlp_download_finished` knows to show a restart dialog instead of
re-running first-launch setup, then `os.execl`s the app to restart in place.
`_check_for_app_updates` does the same pattern for the app itself but just
opens the GitHub releases page (no self-replace) via `webbrowser.open`.

**Settings persistence:** `_save_settings()`/`_load_settings()` read/write JSON
(`{"save_path", "cookies_path"}`) to `QStandardPaths.AppLocalDataLocation` (NOT
the repo's `config.json`, which is just a stray sample file — don't confuse
the two). Saved on every change and on `closeEvent`.

## Gotchas / Things to Know Before Changing Code

- All `yt-dlp.exe`/`ffmpeg.exe` subprocess calls assume the binaries are in the
  **current working directory** (`resource_path()` handles the PyInstaller
  `_MEIPASS` case for bundled resources like icons, but the subprocess calls in
  `workers.py` use bare `"yt-dlp.exe"` / relative paths — this works for the
  built EXE because PyInstaller `--onefile` extracts next to itself at runtime,
  but can break if run from source with a different CWD).
- The formats table's video+audio pairing logic (`_populate_formats_table`) is
  the most complex/fragile part of the UI code — it's where the v2.1.1
  "no audio on 1080p+" bug lived (see Changelog). Any change to format
  filtering/selection should be manually tested against a video with
  multiple audio-language tracks and one without.
- `is_updating_ytdlp` flag on the main window distinguishes "first-time
  setup download" vs "user-triggered update" so the finish handler shows the
  right dialog — don't remove without preserving that branch.
- The app hard-restarts itself (`os.execl`) after any dependency download to
  pick up the new binary — expect the window to visibly relaunch during testing.

## Changelog (bug fixes & features — newest first)

Keep entries short: version/date, what changed, why, where.

### 2026-09-04 (post-v2.3.0) — fix: clip + parallel-fragments combo near-stalls; not in the tagged v2.3.0 build
- **fix (real bug, found after user re-tested the force-keyframes fix above
  and reported it was "still very long" despite the fix landing):** the
  force-keyframes fix above solved the *encoding* hang, but the user's
  test had **both** "Download Clip Only" and "Faster Downloads (Parallel
  Fragments)" checked at once. Reproduced via a scripted diagnostic
  (queuing a real download with `clip_start`/`clip_end` *and*
  `concurrent_fragments=4` together, no GUI): after ~7 minutes the
  `ffmpeg` process was still alive but `Get-Process` showed only 3.15s of
  accumulated CPU time total — i.e. essentially stalled, not merely slow.
  `--download-sections` (a targeted HTTP range request) and
  `-N`/`--concurrent-fragments` (splitting one stream into N parallel
  range requests) apparently interact badly — worse than either flag
  alone, which each work fine individually.
  **Fix:** `main.py` `_on_clip_checkbox_toggled` now unchecks and disables
  the parallel-fragments checkbox whenever clip mode is turned on (re-
  enabled when clip mode is turned back off), with a tooltip explaining
  why (`localization.py` `PARALLEL_FRAGMENTS_CLIP_CONFLICT_TOOLTIP`).
  Verified via scripted check: toggling `clip_checkbox` to `True` flips
  `parallel_fragments_checkbox` to unchecked *and* disabled; toggling back
  off re-enables it. `pytest tests/ -q` still 14/14 passing (no test
  coverage added for this specific interaction since it needs a real
  multi-minute network download to reproduce, not something worth doing
  in CI — the UI-level prevention is the actual fix).
  **Note:** this fix was made *after* the `v2.3.0` tag was already pushed
  and its release build completed — the tagged v2.3.0 installers do
  **not** include it. Flagged to the user; whether it ships as a v2.3.1
  patch or waits is their call, not assumed.

### 2026-09-04 (v2.3.0) — fix: clip downloads looked hung for anything longer than ~30s
- **fix (real bug, found by the user testing a real 6-minute clip):**
  `--force-keyframes-at-cuts` (added in the clip-download feature below)
  does **not** just touch up the cut points — it re-encodes the *entire*
  selected range with libx264, end to end. For a short test clip (10s)
  that's instant, which is why it looked fine when this was first built
  and verified. For the user's real 6-minute 1080p60 clip it meant ~21
  minutes of CPU-bound encoding at the observed `speed=0.28x` — and worse,
  during that whole phase the app's progress regex (`\[download\]\s+N%`)
  never matches ffmpeg's own `frame=... speed=...` progress lines, so the
  UI showed zero feedback ("Waiting...", 0%) for the entire encode. From
  the user's side that is indistinguishable from a genuine hang.
  **Root-caused by reproducing the exact command directly via the yt-dlp
  CLI** (same format ids, same clip range, same flags the app builds) with
  output going to a real log file (piping through `tail` first hid this —
  `tail` buffers until EOF, so nothing appeared until the process
  finished, which looked like *no output at all* and pointed at the wrong
  cause initially). The direct log showed ffmpeg actively transcoding
  frame-by-frame at low speed, not a hang.
  **Fix:** `workers.py` `_clip_section_args()` no longer adds
  `--force-keyframes-at-cuts`. Without it, yt-dlp stream-copies and snaps
  cut points to the nearest keyframe (typically within a couple of
  seconds) instead of frame-accurate cuts — trading a small amount of
  boundary precision for a clip download that is actually fast, which is
  the entire point of the feature. **Re-verified with the identical
  real-world command** that previously hung: now completes in 3m21s for a
  162MB clip (844KB/s, fully proportional to real download bandwidth, not
  stuck), vs. still running with zero progress after 90+ seconds before.
  **Lesson:** the original clip-download testing only used a 10-second
  clip, which was too short to expose a cost that scales with clip
  *length* rather than clip *count* — a good reminder to test with an
  input shape closer to how a feature will actually be used, not just the
  cheapest case that proves the mechanism works at all.

### 2026-09-04 (v2.3.0) — parallel-fragment downloads (opt-in, off by default)
- **feat:** "Faster Downloads (Parallel Fragments)" checkbox next to the
  other download-time toggles. When on, adds yt-dlp's `-N 4`
  (`--concurrent-fragments`, `PARALLEL_FRAGMENTS_COUNT` class constant on
  `SmartVideoDownloader`) to the download command — fetches multiple
  fragments of a DASH/HLS video concurrently instead of one at a time.
  Wired through `main.py`'s `_start_download_worker`/`_on_mp3_row_clicked`/
  `_on_playlist_download_clicked` → request dict → `_launch_download` →
  `DownloadWorker`/`Mp3DownloadWorker` (new `concurrent_fragments` param on
  both, `workers.py`), same plumbing pattern as `embed_subs`/`clip_start`.
  **Deliberately shipped off by default, not as the "free speed win" it's
  often described as:** measured it directly before implementing anything
  — a real A/B (`-N 1` vs `-N 8`, same 1080p YouTube format, same session)
  took 3m17s sequential vs **4m38s concurrent, i.e. slower**. Both runs
  showed heavy, bursty near-zero-then-spike throttling patterns typical of
  YouTube-side rate-limiting; the working theory is that opening more
  simultaneous connections against a server-throttled source doesn't
  increase aggregate throughput and just adds connection overhead. This
  isn't a fully controlled test (sequential runs, not simultaneous, so
  network conditions could have shifted between them) but it directly
  contradicts the assumption that concurrency is a strict win, so it's
  presented to users as an option to try, not a default that could make
  someone's downloads slower without them knowing why. May still help on
  sites/CDNs that don't throttle per-connection the way YouTube did in
  this test.

### 2026-09-04 (v2.3.0) — clip/time-range downloading
- **feat: download just a portion of a video** ("Download Clip Only"
  checkbox in the formats section, next to the embed checkboxes). Reveals
  Start/End `mm:ss` inputs plus a "Video length: H:MM:SS" hint sourced from
  `fetched_data['duration']`. `main.py` `_get_clip_range()` validates and
  parses the inputs (`_parse_time_to_seconds`, accepts `SS`/`MM:SS`/`H:MM:SS`),
  returning `(None, None)` when the checkbox is off, `False` (with an error
  already shown) if on but invalid, else `(start_seconds, end_seconds)`.
  Wired into both `_on_download_clicked` and `_on_mp3_row_clicked` (not
  playlist bulk downloads, out of scope for this pass) — appends a
  `[XmYYs-XmYYs]` tag to the filename so a clip never collides with a
  full-video download of the same title, and a matching `[Clip H:MM–H:MM]`
  note in the queue-item label.
  `workers.py`: new `_clip_section_args()` helper builds
  `--download-sections "*START-END"` (seconds, not timestamps, to sidestep
  any format ambiguity) — added as an optional `clip_start`/`clip_end`
  param on both `DownloadWorker` and `Mp3DownloadWorker`.
  **Correction (see the fix entry above, newer):** this originally also
  added `--force-keyframes-at-cuts` for frame-accurate cut boundaries; that
  was based on a misreading of what the flag does (assumed it only
  touched up the cut points) and was removed after it made real-world clip
  downloads look hung for minutes. Cuts now snap to the nearest keyframe
  instead of being frame-accurate — the right trade-off for a feature
  whose whole point is speed.
  Verified the exact yt-dlp syntax and behavior directly via the CLI before
  wiring it up (confirmed `*30-40` on a real video downloads only that
  range, not the full video, then trims), then verified the full app flow
  end-to-end with a scripted test (not GUI clicking, per user preference
  during this session): queued a real download with `clip_start=30,
  clip_end=40` through the actual `_queue_download`/`_launch_download`
  pipeline, waited for completion, and confirmed via `ffmpeg -i` that the
  output file's duration was exactly `00:00:10.00`.

### 2026-09-04 — v2.2.0 shipped without macOS Intel (runner scarcity) + "Show in Folder" button
- **v2.2.0 shipped as Windows + macOS Apple Silicon only.** `build-macos-intel`
  never got a runner from GitHub's `macos-13` pool — queued 27+ minutes,
  confirmed via githubstatus.com there was no active incident, just genuine
  Intel-runner scarcity as GitHub shrinks that fleet. Cancelled the stuck
  run, downloaded the two artifacts that *had* finished (`build-windows`,
  `build-macos-arm64`) via `gh run download`, and published the v2.2.0
  GitHub Release manually with `gh release create` using just those two.
  Removed the Intel badge/link/install-step wording from `README.md` so
  nothing points at a nonexistent asset, left a one-line "planned for a
  future release" note. The `release.yml` workflow itself is unchanged and
  still tries all three platforms on the next tag.
- **feat: "Show in Folder" button.** Reuses the existing queue-item action
  button slot (previously hidden on success) — on a completed download it
  now shows this instead, wired through the same `_on_queue_item_action_clicked`
  dispatcher that already handles Cancel/Retry (adds a third branch keyed on
  `item.state == "completed"`). New `main.py` `_reveal_in_file_manager(path)`
  helper: Windows uses `explorer /select,"path"` (falls back to just opening
  the containing folder via `os.startfile` if the exact file is missing),
  macOS uses `open -R path` (or plain `open` on the folder as fallback).
  Verified live through the actual GUI: downloaded a real video, clicked
  "Show in Folder", watched File Explorer open directly to Downloads with
  the file pre-selected.

### 2026-09-04 — startup clipboard check + a real CI hang caught right after tagging v2.2.0
- **feat:** The clipboard "Paste copied link?" hint (see v2.2.0 entry below)
  only checked on window *re*-activation, not on first launch. Added a
  `showEvent` override (guarded by `self._startup_clipboard_checked` so it
  only fires once) that runs the same check on startup.
- **fix (CI): the new `tests/` suite hung indefinitely in GitHub Actions.**
  Caught this immediately after pushing the v2.2.0 tag — the release build
  jobs succeeded, but the new `Tests` workflow sat "in progress" for 10+
  minutes on a suite that runs in under a second locally. Root cause:
  `make_window()`'s fixture instantiates the real `SmartVideoDownloader`,
  whose `__init__` calls `check_dependencies()` — which, when `yt-dlp`/
  `ffmpeg` don't exist (the CI checkout never fetches them, same as any
  fresh clone), shows a blocking `ModalDialog(...).exec()` asking to
  download-or-exit. Under a headless/offscreen `QApplication` with no user
  to click it, that `.exec()` blocks forever. This never showed up locally
  purely because the real binaries already happen to sit in this working
  tree. **Verified the exact failure mode by reproducing it locally**:
  temporarily moved `yt-dlp.exe`/`ffmpeg.exe` out of the repo folder and
  ran `pytest` under a hard `timeout` — confirmed it hung on literally the
  first test with exit code 124, matching the CI symptom precisely. Fixed
  by stubbing `check_dependencies` to a no-op via `monkeypatch` in the
  `make_window` fixture (`tests/conftest.py`) — these tests only exercise
  formats-table/worker logic, never the startup dependency flow, so this
  is the correct fix, not a workaround. Re-verified the same way (binaries
  moved out, hard timeout): 14/14 pass in 0.43s. Cancelled the hung
  workflow run via `gh run cancel` before it burned more CI minutes.
  **Lesson:** a test fixture that happens to pass locally because of
  incidental local state (binaries already present, in this case) needs to
  be verified against the state CI will actually see, not just re-run
  in-place — this is the same "verify in the target environment, not just
  around it" mistake class as the yt-dlp-wrong-binary bug earlier today.

### 2026-09-04 (v2.2.0) — playlist support, cancel/retry, embedding, tests, Intel Mac CI, clipboard hint
- **feat: playlist support ("simple" mode).** New `PlaylistProbeWorker` in
  `workers.py` runs `yt-dlp <url> --flat-playlist --no-playlist --dump-json
  --no-warnings` — cheap (no per-video format data) and, critically,
  `--no-playlist` is combined with `--flat-playlist` deliberately: verified
  directly via the yt-dlp CLI that a URL carrying both a video id and a list
  id (e.g. `watch?v=X&list=Y`, extremely common when a video is opened from
  inside a playlist) needs `--no-playlist` to still isolate just that one
  video even in flat mode — without it, `--flat-playlist` alone enumerates
  the *entire* playlist for that same URL, which would have silently broken
  single-video fetches for anyone who followed a video from a playlist. A
  pure playlist URL (no isolatable single video) still gets fully enumerated
  regardless. `main.py` `_on_fetch_clicked` now probes first: exactly 1
  entry → falls through to the existing single-video `FetchWorker` flow
  completely unchanged; >1 entries → new `_create_playlist_section` panel
  (checkboxes + a single quality-target dropdown: Best/1080p/720p/480p/Audio
  MP3 + Select All/Deselect All + Download Selected). Each selected video is
  translated into a plain yt-dlp format-selector string (e.g.
  `bestvideo[height<=1080]+bestaudio/best[height<=1080]`) and queued through
  the *same* download-queue machinery as single-video downloads — no
  separate code path, so cancel/retry (below) works for playlist items too.
- **feat: cancel + retry on queue items.** `DownloadWorker`/
  `Mp3DownloadWorker` now expose a `cancel()` method (`self.process.terminate()`)
  and a `cancelled` flag so a cancelled download reports a distinct
  `"Cancelled"` result rather than a generic failure. `DownloadItem` gained
  an action button (Cancel while running → Retry after failure/cancel).
  Retrying re-invokes the same worker with the same save path, so it
  resumes from the partial file via yt-dlp's default `--continue` behavior
  rather than restarting — this is the practical equivalent of "pause",
  since yt-dlp's streaming model has no clean way to literally pause an
  in-flight HTTP transfer without killing the process.
  **Fixed the original bug this was requested for:** a failed download used
  to leave its formats-table row's Download button stuck on "Queued"
  forever (`_on_download_finished` never touched it). Now tracked via a new
  `self.download_source_buttons` dict and re-enabled on failure.
  **Found and fixed a real crash while building this, twice:**
  1. `_launch_download`'s `QThread` was a local variable with no persistent
     Python reference (`thread = QThread()`, never stored on `self`) — PyQt
     can garbage-collect a `QThread` wrapper while the underlying C++ thread
     is still executing, which crashed the process with **zero Python
     traceback** on literally the first real download. Caught via a direct
     scripted repro (`_queue_download` → immediate silent exit code 127) with
     incremental flushed print statements to isolate exactly which line it
     died on. Fixed by keeping every launched thread alive in `self.active_threads`.
  2. Even after that fix, retrying a cancelled download under the same
     `unique_id` *also* crashed intermittently: `_on_download_finished`
     (which flips the UI to "cancelled"/retryable) runs on an earlier
     event-loop pass than the `QThread`'s own `finished` signal (which
     actually stops the thread) — so a dict keyed by `unique_id` could have
     its entry overwritten by the *new* thread on retry while the *old*
     thread hadn't confirmed it was done yet, dropping the last reference
     to a QThread that might still be alive. Fixed by using a list that
     only removes a thread once *that thread's own* `finished` signal
     fires, instead of a dict keyed by something that gets reused.
     Both fixes verified via a direct scripted queue→cancel→retry cycle
     (not just manual GUI clicking) before trusting them, then re-verified
     live through the actual GUI end-to-end (real 232MB 4K download,
     Cancel mid-transfer, Retry, completed — file confirmed on disk).
- **feat: subtitle + thumbnail/metadata embedding (opt-in, default off).**
  Two new checkboxes next to the Quality/Format/Language filter row.
  `DownloadWorker`/`Mp3DownloadWorker` gained `embed_subs`/`embed_metadata`
  params that extend the yt-dlp command with `--write-subs --sub-langs
  "en.*,und" --embed-subs` and/or `--embed-thumbnail --embed-metadata`
  (ffmpeg-dependent, already a hard requirement of this app). MP3 downloads
  get subtitles written as a sidecar file only (embedding a subtitle stream
  into an MP3 container isn't meaningful), not `--embed-subs`.
- **feat: clipboard "Paste copied link?" hint.** `SmartVideoDownloader`
  overrides `changeEvent` and checks the clipboard on `ActivationChange`
  (i.e. when the window becomes active again — no background polling/timer).
  If it holds a URL that differs from the current input and from the last
  offered/dismissed value, shows a small dismissible label above the URL
  box; clicking it fills the field (never auto-fetches); typing manually
  also dismisses it. Verified live by setting the clipboard externally and
  minimizing/restoring the window to trigger the activation event.
- **feat: automated test suite** (new `tests/` dir + `.github/workflows/test.yml`,
  running on every push/PR to `main`, separate from the tag-triggered release
  pipeline). Targets the exact class of bug that has repeatedly shipped in
  this file's own history (three real bugs in the formats-table/pairing
  logic across one earlier session): hand-built fixture JSON files
  (single format, multi-resolution × multi-language, audio tracks with
  `"abr": null`) run through the real `_populate_formats_table`/
  `_add_format_row` code via a headless (`QT_QPA_PLATFORM=offscreen`)
  `QApplication`, plus pure-logic tests for `get_bin_dir`/path resolution
  and the new `parse_flat_playlist_output` helper. No subprocess or network
  calls in any test. 14/14 passing.
- **feat: Intel Mac CI build.** Added `build-macos-intel` (`macos-13`) to
  `release.yml`, mirroring the existing Apple Silicon job, producing
  `SmartVideoDownloader-macOS-x86_64.dmg`. `publish-release` now depends on
  and attaches all three installers. A single `universal2` build could
  replace both mac jobs (PyQt6 does publish universal2 wheels), but
  verifying that actually works needs real Mac hardware to debug if it
  doesn't — going with two separate, predictable per-arch builds instead,
  same reasoning as the original arm64-only decision.
- **chore:** `README.md` updated (playlist/cancel-retry/embedding/clipboard
  features listed, second macOS Intel download button + install note);
  `.gitignore` gained `.pytest_cache/`.
- All of the above was implemented and verified (pytest + live GUI
  end-to-end for every feature) *before* being committed — per an explicit
  checkpoint agreed with the user, the version bump/commit/tag/push only
  happened after they confirmed v2.2.0 and gave the go-ahead.

### 2026-09-04 (v2.1.2) — Language filter + genuine Windows/macOS cross-platform support + release CI
- **feat:** Added a **Language** filter to the formats table, alongside the
  existing Quality/Format filters (`main.py`). Each row is tagged with its
  audio language via `QTableWidgetItem.setData(Qt.ItemDataRole.UserRole, ...)`
  on the Quality-column cell (`_add_format_row`); `_populate_formats_table`
  collects the set of languages present and populates the new
  `self.language_filter` combo box; `_filter_table` matches against it, with
  rows that have no language (merged formats, the MP3 row) always passing
  since they aren't language-specific. Along the way, fixed a small
  pre-existing gap where pure audio-only rows showed no language at all in
  their Note text.
- **feat (major): the app is now genuinely cross-platform (Windows + macOS
  Apple Silicon), not Windows-only.**
  - `workers.py`: `YTDLP_PATH`/`FFMPEG_PATH` now use a conditional
    `EXE_SUFFIX` (`.exe` on Windows, none on mac) instead of a hardcoded
    `.exe`. Added a module-level `CREATE_NO_WINDOW = getattr(subprocess,
    "CREATE_NO_WINDOW", 0)` and replaced every direct
    `subprocess.CREATE_NO_WINDOW` reference with it — that constant doesn't
    exist on macOS/Linux and would have raised `AttributeError`.
  - `config.py`: added `YT_DLP_URL_MAC` (yt-dlp's official `yt-dlp_macos`
    release asset — a direct executable, no zip) and `FFMPEG_URL_MAC`
    (`evermeet.cx`'s stable "always latest" zip endpoint, the same role
    BtbN plays for Windows). `YTDlpWorker`/`FFmpegDownloadWorker` pick the
    right URL based on `IS_MAC` (`sys.platform.startswith("darwin")`) and
    `chmod 0o755` the downloaded binary on mac (needed there, not on
    Windows). Verified both URLs resolve to real assets by fetching them
    directly before wiring this up.
  - `FFmpegDownloadWorker`'s zip extraction now branches by platform: the
    Windows BtbN build nests the binary at `.../bin/ffmpeg.exe`; the mac
    evermeet.cx build has a single root-level member literally named
    `ffmpeg` (verified this by actually downloading and inspecting the real
    zip — an earlier assumption of a nested `bin/ffmpeg` path was wrong and
    would have silently matched nothing). Both branches move the extracted
    file into place with `os.replace` (not `os.rename` — see the
    self-repair entry above for why that matters on Windows; the same
    hazard applies on mac).
  - Binaries are *not* bundled into the installer on either platform — the
    app downloads them itself on first launch via the existing
    dependency-check flow, so no build-time fetching was needed.
- **feat: macOS packaging.** No `.icns` icon existed (and can't be generated
  on Windows); it's generated at CI build time from the existing `icon.png`
  via macOS's built-in `sips`/`iconutil`. No new PyInstaller spec file was
  added — `*.spec` is `.gitignore`d in this repo (regenerated per-build, not
  version-controlled) and PyInstaller's `--windowed` flag already produces a
  proper `.app` bundle on macOS automatically from the same CLI command
  pattern already documented for Windows, so the mac CI job just runs that
  CLI command with `icon.icns` and a `:`-separated `--add-data` (Windows
  uses `;`). Packaged into a `.dmg` via macOS's built-in `hdiutil` (no extra
  dependency).
- **feat: GitHub Actions release pipeline** (`.github/workflows/release.yml`,
  new). Triggers on `v*` tag pushes (plus manual `workflow_dispatch`).
  `build-windows` (windows-latest): PyInstaller → installs Inno Setup via
  `choco` → compiles `setup_script.iss`. `build-macos` (pinned to
  `macos-14`/Apple Silicon, not the floating `macos-latest` alias, for
  architecture stability): generates the icon → PyInstaller → `hdiutil`.
  `publish-release` (needs both): attaches both installers to the GitHub
  Release via `softprops/action-gh-release`. Artifact filenames are
  **version-agnostic** (`SmartVideoDownloaderSetup-Windows.exe`,
  `SmartVideoDownloader-macOS-arm64.dmg` — no version number in the name)
  specifically so README links to `/releases/latest/download/<filename>`
  never go stale across releases.
- **fix (blocking prerequisite for any of the above to work in CI):**
  `requirements.txt` listed `PyQt5` (wrong — the app has imported `PyQt6`
  since the v2.0 refactor, already flagged as stale in this file's Gotchas
  section) and was missing `requests`/`packaging`, both imported by
  `workers.py`. Fixed to `PyQt6`, `yt-dlp`, `requests`, `packaging`.
- **fix:** `setup_script.iss` hardcoded absolute paths
  (`C:\ADNAN\YT-Downloader\...`) that were already stale even for local
  builds on this machine (the repo lives at `E:\Claude-Tools\YT-Downloader`)
  and would never have worked in CI regardless. Changed to paths relative to
  the `.iss` file's own directory (Inno Setup's default resolution), and the
  output filename to the version-agnostic `SmartVideoDownloaderSetup-Windows`
  mentioned above.
- **chore:** bumped `APP_VERSION` `v2.1.1` → `v2.1.2` (`config.py`,
  `setup_script.iss`), updated `README.md` (dynamic latest-release badge,
  separate Windows/macOS download buttons and install sections, macOS
  Gatekeeper workaround instructions covering both the classic right-click
  flow and the newer macOS Sequoia+ System Settings flow since Apple changed
  this across versions), and `.gitignore` (added `Output/`, `*.dmg`,
  `*.icns` — these are build outputs, never meant to be committed).
- **Known limitation, called out explicitly to the user:** this was
  implemented and CI-verified (the Actions run succeeding is real signal),
  but actual runtime behavior on physical Mac hardware — does the app
  launch, does the documented Gatekeeper flow match reality — could not be
  verified directly; no macOS machine was available this session. Also,
  only Apple Silicon (arm64) is targeted; Intel Macs are unsupported by
  design per this session's discussion with the user (cost/complexity
  tradeoff of a second CI job), not an oversight — revisit if Intel-Mac
  users report needing it.

### 2026-09-04 — automatic yt-dlp/ffmpeg update checks + self-repair for corrupted binaries
- **feat:** User asked, after the wrong-binary bug above, to make sure the app
  always checks for yt-dlp/ffmpeg updates and can never again silently run a
  broken/stale copy. Added:
  - **Automatic yt-dlp version check on every startup** (silent, alongside the
    existing silent app-update check in `check_dependencies()`). Reuses the
    existing `VersionCheckWorker` (already used by the manual "Update yt-dlp"
    menu action) via a new shared `_start_ytdlp_version_check(silent)` method
    in `main.py`. If an update is available, the same prompt dialog as the
    manual flow appears (download & restart, or skip); if already up to date,
    stays fully silent — matches the existing app-update-check UX pattern
    exactly (`_check_for_app_updates`/`_on_app_update_checked`).
  - **Corruption self-repair for both yt-dlp and ffmpeg.** `VersionCheckWorker`
    already returns `local_version == "N/A"` if `yt-dlp.exe --version` fails
    to run even though the file exists — repurposed that as a corruption
    signal: `_on_ytdlp_version_checked` now detects "file exists but won't
    run" and auto-triggers a fresh download + restart (with a brief
    heads-up dialog, since it's a repair action, not a routine background
    check). Added the equivalent for ffmpeg: a new `FFmpegHealthCheckWorker`
    in `workers.py` (runs `ffmpeg.exe -version`, emits a bool via a new
    `ffmpeg_health_checked` signal) wired up through `_check_ffmpeg_health`/
    `_on_ffmpeg_health_checked` in `main.py`, called from `check_dependencies()`
    alongside the yt-dlp check. Directly addresses the user's ask: a
    corrupted/broken bundled binary can no longer cause a silent bad state —
    it gets detected and replaced automatically on next launch.
  - Added `FFMPEG_CORRUPT_REDOWNLOADING`/`YTDLP_CORRUPT_REDOWNLOADING` strings
    to `localization.py`.
  - **Found and fixed a real (pre-existing, previously untriggered) bug while
    testing this:** `FFmpegDownloadWorker`'s extraction step used
    `os.rename(extracted_file, FFMPEG_PATH)` to move the freshly-extracted
    `ffmpeg.exe` into place. `os.rename` raises `FileExistsError` on Windows
    if the destination already exists — harmless during first-time setup
    (no `ffmpeg.exe` there yet) but fatal during a *repair*, where the
    corrupted `ffmpeg.exe` is already sitting at that exact path. Caught this
    via a live end-to-end test (corrupted `ffmpeg.exe`, watched the app
    detect it, download the full ~192MB build, then fail at the final move
    step and delete the downloaded zip via the except-block cleanup, leaving
    the corrupted file in place). **Fix:** changed to `os.replace(...)`,
    which atomically overwrites the destination on both Windows and POSIX.
    Verified via a targeted simulation of the exact same extraction code
    with a pre-existing "corrupt" target file in place (avoided repeating
    the full 192MB download a second time) — confirmed the new file
    correctly overwrites the old one. The yt-dlp side of this never had the
    same bug because its download path uses `open(YTDLP_PATH, "wb")`
    directly, which always overwrites regardless of OS.
  Verified end-to-end live through the actual GUI: corrupted the real
  `yt-dlp.exe` → app detected it on startup, showed the repair dialog,
  redownloaded, and restarted cleanly with a working binary. Confirmed a
  clean/healthy startup afterward shows no false-positive dialogs.

### 2026-09-04 — two more layered bugs found while chasing "still 360p only": wrong yt-dlp binary + a real crash in the formats table
- **context:** After the `player_client` correction below, the user reported the
  table was *still* stuck at 360p on the actual running `python main.py` app
  (not the stale installed EXE — that was a dead-end theory, ruled out). Root
  cause turned out to be two independent, previously-latent bugs stacked on
  top of each other:
  1. **Wrong yt-dlp binary picked up.** `workers.py` invoked the bundled
     binary via the bare name `"yt-dlp.exe"` everywhere (existence checks,
     downloads, and all three subprocess calls), relying on Windows'
     executable search order to find it via cwd. In practice Windows was
     resolving that bare name to an unrelated **pip-installed yt-dlp
     (2026.02.04)** sitting on system PATH at
     `...\Python\Python313\Scripts\yt-dlp.exe`, *not* the repo's own
     2026.08.19 binary — confirmed by directly replicating `FetchWorker`'s
     exact `subprocess.run` call and seeing its stderr self-report as
     "2026.02.04" plus a "no supported JavaScript runtime" warning. That
     stale copy couldn't resolve most formats, so it silently fell back to
     the one legacy format it could: 360p. This exactly matches the gotcha
     already documented in this file's Gotchas section about bare relative
     binary paths breaking when run from source.
     **Fix:** added `get_bin_dir()` to `workers.py` (frozen → dir of
     `sys.executable`; from source → dir of `workers.py` itself) and
     `YTDLP_PATH`/`FFMPEG_PATH` absolute-path constants built from it. Every
     bare `"yt-dlp.exe"`/`"ffmpeg.exe"` reference in `workers.py`
     (`VersionCheckWorker`, `YTDlpWorker`, `FFmpegDownloadWorker`,
     `FetchWorker`, `DownloadWorker`, `Mp3DownloadWorker`) now uses these
     constants instead of a bare name, so the app always runs its own
     bundled binary regardless of cwd/PATH. `main.py`'s `ffmpeg_found`/
     `ytdlp_found` checks (`__init__` and `check_dependencies`) were updated
     to import and use the same constants instead of `resource_path(...)`,
     which was also wrong for these two files specifically (they live next
     to the built EXE, not inside PyInstaller's `_MEIPASS`, since they're
     not bundled via `--add-data`).
  2. **Real crash in `_populate_formats_table` once full format data actually
     arrived.** With the binary bug fixed, fetching returned the full
     format list — and the app then crashed outright a few seconds after
     every single Fetch, with **no Python traceback at all** (silent native
     abort from an unhandled exception inside a Qt slot). Isolated by
     calling `FetchWorker.run()` and `_populate_formats_table()` directly
     in a script (bypassing the GUI event loop) to get a real traceback:
     `TypeError: '>' not supported between instances of 'NoneType' and
     'NoneType'` at `main.py`'s `best_audio = max(audio_formats, key=lambda
     a: a.get('abr', 0))`. Cause: `.get('abr', 0)` only substitutes the
     default `0` when the `'abr'` key is *missing* — but many real
     audio-only formats have the key present with value `None` (bitrate not
     computed for that stream), so `.get()` returns `None`, and comparing
     `None` to `None` blows up `max()`/`sorted()`. This bug is genuinely old
     (predates today's session) but was masked until now: the earlier
     wrong-binary bug happened to return a single *muxed* format with no
     separate `audio_formats` list, so this code path was simply never
     exercised by any of today's earlier tests.
     **Fix:** changed both call sites in `_populate_formats_table` from
     `a.get('abr', 0)` to `a.get('abr') or 0` (handles missing key *and*
     explicit `None` value).
  Verified end-to-end via a direct scripted fetch + populate (925 rows for
  a heavily-dubbed video: 37 video resolutions 144p–2160p × 21 audio
  languages) and then live through the actual GUI — full quality dropdown
  now shows 2160p/1440p/1080p/720p/480p/360p/240p/144p/Audio, no crash.
  **Lesson for future sessions:** when a fetch "succeeds" but shows
  suspiciously little data, don't assume yt-dlp itself is the problem —
  verify the *exact* binary path being invoked (`--version` output can
  reveal a different binary than expected) AND replicate the GUI's
  post-fetch data processing directly in a script outside the Qt event
  loop, since exceptions raised inside a Qt slot can silently kill the
  whole process with zero traceback output.

### 2026-09-04 — correction: forced `player_client` broke format selection (4K/HD/multi-audio gone)
- **fix:** The 403 fix below (forcing `--extractor-args
  "youtube:player_client=android,web,ios"`) had an unintended side effect
  reported by the user after testing: the formats table collapsed to just
  360p + MP3, losing 4K/1440p/1080p/720p video and all the extra audio-only
  tracks that used to show up. Root cause: the `android` client YouTube serves
  does **not** return the DASH manifest at all — it only exposes one legacy
  progressive itag (18, 640x360 with muxed low-quality audio). Since `android`
  was first in the client list and succeeded, yt-dlp never needed to fall
  back to `web`/`ios`, so every fetch silently got android's crippled format
  list. Verified via direct CLI compare: `--list-formats` with
  `player_client=android,web,ios` → only itag 18; with no override at all →
  37 video-only formats (144p–2160p) + 7 audio-only formats.
  **Also re-verified the original 403 premise:** with the bundled `yt-dlp.exe`
  now updated (`2026.08.19`), the *default* client rotation (currently landing
  on `visionos`) reliably returns full formats AND downloads a 1080p stream
  without any 403, across repeated runs, and MP3 extraction works too. This
  strongly suggests the original 403 was caused by the **stale yt-dlp binary**
  (`2025.11.12`), not by needing a specific client — the client-forcing part of
  the earlier fix was an overcorrection.
  **Fix:** removed `--extractor-args "youtube:player_client=android,web,ios"`
  from all three yt-dlp invocations in `workers.py` (`FetchWorker`,
  `DownloadWorker`, `Mp3DownloadWorker`), restoring default client rotation.
  If 403s return in the future, keeping `yt-dlp.exe` current is the first
  thing to check before reaching for a client override again — and if a
  client override does become necessary, verify with `--list-formats` (not
  just one download) that it still returns the full resolution/audio range,
  since some clients (like `android`) silently truncate the format list.

### 2026-09-04 — yt-dlp `403 Forbidden` on download (root-caused + fixed)
- **fix:** Downloads (and MP3 conversions) were intermittently/consistently
  failing with `ERROR: unable to download video data: HTTP Error 403:
  Forbidden`, even though "Fetch" worked fine. Root-caused via direct
  `yt-dlp.exe` CLI testing: yt-dlp's default YouTube player-client rotation
  was landing on `android_vr` (and, later in testing, `visionos`) — both
  currently blocked/broken by YouTube — while other clients (`android`,
  `web`, `ios`) resolved and downloaded the same formats without issue.
  Confirmed reproducible by forcing `--extractor-args
  "youtube:player_client=android_vr"` (fails) vs `player_client=android,web,ios`
  (succeeds reliably, verified with several repeat downloads).
  **Fix:** added `--extractor-args "youtube:player_client=android,web,ios"` to
  all three yt-dlp invocations in `workers.py` (`FetchWorker`, `DownloadWorker`,
  `Mp3DownloadWorker`). Verified end-to-end through the actual GUI (fetch →
  format table → Download click → progress → "1/1 completed" → real file on
  disk). This is a YouTube/yt-dlp extractor cat-and-mouse issue (client
  breakage changes over time), not an app logic bug — if downloads start
  403'ing again in the future, the fix is to update this client list (check
  which clients currently work via `yt-dlp.exe <url> --extractor-args
  "youtube:player_client=<name>" --simulate`), not to touch the download flow.
- **chore:** Bundled `yt-dlp.exe` was also very stale (`2025.11.12` vs latest
  `2026.08.19` at the time) and was updated in the working tree. Bundled
  binaries are gitignored (`*.exe`), so this isn't a commit — just a note that
  whoever builds the next release should re-run the yt-dlp update flow (or
  redownload) before packaging.
- **known non-blocking issue found during this testing pass (not fixed):**
  after a download fails, its row's Download button stays permanently
  disabled/stuck on "Queued" (`_on_download_finished` never re-enables it),
  so retrying requires a full re-fetch. `main.py` `_start_download_worker` /
  `_on_download_finished`.

### Unresolved / uncommitted at last handoff (2026-09-04)
- **fix:** `is_updating_ytdlp` flag added to `SmartVideoDownloader` (`main.py`)
  so that clicking "Update yt-dlp" from the menu, then completing the download,
  shows a proper success/restart dialog instead of silently re-running
  `check_dependencies()` (which is meant only for first-launch setup). Previously
  `_on_ytdlp_update_clicked` → `_start_ytdlp_download(for_update=True)` set a
  `for_update` flag that was never actually read by the finish handler, so a
  manual yt-dlp update looked like it did nothing.
  Files: `main.py` (`__init__`, `_on_ytdlp_download_finished`, `_on_ytdlp_version_checked`).
- **chore:** `config.py` `APP_VERSION` bumped `v2.1.0` → `v2.1.1` (uncommitted
  as of this handoff — commit alongside the fix above when ready).
- These changes are **staged in the working tree but not committed** as of
  this handoff — verify `git status` before continuing work.

### v2.1.0/v2.1.1 (2025-11-21)
- **fix (critical):** Corrected audio merging bug where downloads of
  high-resolution videos (1080p+) had no audio. Root cause was in how video-only
  formats were paired with a separate audio stream and merged via
  `--merge-output-format mp4`; multiple follow-up commits under the same message
  ("Correct critical audio merging bug and other minor fixes") iterated on the
  fix in `workers.py` (`DownloadWorker`) and `main.py` (`_populate_formats_table`,
  `_add_format_row`).
- **fix:** Resolved several `TypeError`/`AttributeError` crashes left over from
  the v2.0 refactor.
- **fix:** Improved UI consistency and error handling dialogs.

### v2.0.0 (2025-10-30)
- **feat (major):** Full architectural refactor from a single-file app into
  isolated modules: `main.py` (UI), `workers.py` (background work), `config.py`
  (settings/URLs), `theme.py` + `styles.py` (theming), `localization.py` (strings).
- **feat:** Added support for hundreds of additional sites (TikTok, Instagram,
  Facebook, Dailymotion, etc.) via `yt-dlp`'s native extractor list.
- **feat:** Application auto-updater (`AppUpdateCheckWorker` + GitHub releases
  API) and mandatory first-launch dependency downloader for `yt-dlp`/`ffmpeg`
  (`check_dependencies`, `YTDlpWorker`, `FFmpegDownloadWorker`).
  Follow-up fix commits (2025-10-30, "Correct NameError during format
  population") patched crashes introduced by this refactor in the formats
  table population path.
- **feat:** Contextual error handling — private/members-only video detection
  with a dedicated "How to Add Cookies" help dialog (`_show_private_video_help`,
  `PRIVATE_VIDEO_HELP` string).

### Initial release (2025-10-28)
- Initial commit: complete single-pass application source (pre-refactor),
  README, screenshots, license.

---
*Generated 2026-09-04 by Claude as a project handoff. Update the Changelog
section above with every future fix/feature so the next session (human or
Claude) doesn't have to re-derive project history from `git log`.*
