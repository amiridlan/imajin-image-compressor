"""
Auto-update system for Imajin.

Flow:
  UpdateChecker (QThread) ──► update_available(version, url)
                           ──► up_to_date()
                           ──► check_failed()

  UpdateDownloader (QThread) ──► progress(0-100)
                              ──► ready(installer_path)
                              ──► error(message)

  launch_installer(path) — runs the Inno Setup installer silently and exits.
"""

import os
import sys
import tempfile
import subprocess

import requests
from PyQt6.QtCore import QThread, pyqtSignal

# ── Configure these before publishing ─────────────────────────────────
GITHUB_OWNER = "amiridlan"
GITHUB_REPO = "imajin-image-compressor"
# ──────────────────────────────────────────────────────────────────────

_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _parse_version(tag: str) -> tuple[int, ...]:
    """'v2.1.0' or '2.1.0' → (2, 1, 0)"""
    return tuple(int(x) for x in tag.lstrip("v").split("."))


class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)  # latest_version, download_url
    up_to_date = pyqtSignal()
    check_failed = pyqtSignal()

    def run(self):
        try:
            from version import __version__

            r = requests.get(
                _API_URL, timeout=8, headers={"Accept": "application/vnd.github+json"}
            )
            r.raise_for_status()
            data = r.json()

            latest_tag = data.get("tag_name", "")
            if not latest_tag:
                self.check_failed.emit()
                return

            if _parse_version(latest_tag) > _parse_version(__version__):
                # Find the first .exe asset
                asset = next(
                    (
                        a
                        for a in data.get("assets", [])
                        if a["name"].lower().endswith(".exe")
                    ),
                    None,
                )
                if asset:
                    self.update_available.emit(
                        latest_tag.lstrip("v"), asset["browser_download_url"]
                    )
                    return

            self.up_to_date.emit()

        except Exception:
            self.check_failed.emit()


class UpdateDownloader(QThread):
    progress = pyqtSignal(int)  # 0–100
    ready = pyqtSignal(str)  # path to downloaded installer
    error = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            dest = os.path.join(tempfile.gettempdir(), "ImajinSetup.exe")
            with requests.get(self._url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if self._cancelled:
                            return
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            self.progress.emit(int(downloaded / total * 100))
            self.ready.emit(dest)
        except Exception as e:
            self.error.emit(str(e))


def launch_installer(path: str) -> None:
    """Launch the Inno Setup installer silently and exit the running app."""
    subprocess.Popen([path, "/SILENT", "/CLOSEAPPLICATIONS"])
    sys.exit(0)
