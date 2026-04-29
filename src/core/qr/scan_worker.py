from PyQt6.QtCore import QThread, pyqtSignal


class QrScanWorker(QThread):
    """Background thread: scan a file for QR codes + check each URL."""

    scan_completed = pyqtSignal(list)   # list of enriched result dicts
    scan_failed = pyqtSignal(str)       # error message
    status_update = pyqtSignal(str)     # free-form status text

    def __init__(self, file_path: str, virustotal_key: str = ''):
        super().__init__()
        self.file_path = file_path
        self.virustotal_key = virustotal_key

    def run(self):
        try:
            from core.qr.scanner import scan_file
            from core.qr.malware_checker import check_url, is_url

            self.status_update.emit('SCANNING FILE...')
            codes = scan_file(self.file_path)

            if not codes:
                self.scan_completed.emit([])
                return

            self.status_update.emit('CHECKING URLs...')
            results = []
            for i, code in enumerate(codes):
                data = code['data']
                if is_url(data):
                    safety = check_url(data, self.virustotal_key)
                else:
                    safety = {
                        'status': 'unknown',
                        'source': 'n/a',
                        'detail': 'Not a URL — no safety check performed.',
                    }
                results.append({**code, 'safety': safety, 'index': i + 1})

            self.scan_completed.emit(results)
        except Exception as e:
            self.scan_failed.emit(str(e))
