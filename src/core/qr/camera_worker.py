import cv2
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

# Theme.ACCENT #FF2D78 = R255 G45 B120 → BGR for cv2
_ACCENT_BGR = (120, 45, 255)
_SCAN_EVERY_N_FRAMES = 5   # scan for QR on 1 in 5 frames (~6 scans/sec at 30fps)


class CameraWorker(QThread):
    """
    Captures frames from a camera, overlays QR bounding boxes,
    and emits new detections in real time.

    Signals:
        frame_ready(QImage)  – every captured frame, with bounding boxes drawn
        qr_detected(list)    – list of result dicts for newly-seen QR codes
        camera_error(str)    – emitted if camera cannot open or disconnects
    """

    frame_ready   = pyqtSignal(QImage)
    qr_detected   = pyqtSignal(list)
    camera_error  = pyqtSignal(str)

    def __init__(self, device_index: int = 0, virustotal_key: str = ''):
        super().__init__()
        self.device_index    = device_index
        self.virustotal_key  = virustotal_key
        self._running        = False
        self._seen_codes: set = set()
        self._current_rects: list = []   # persisted between scan intervals

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def stop(self):
        self._running = False

    def reset_seen(self):
        """Clear history so already-seen codes can be re-emitted."""
        self._seen_codes.clear()
        self._current_rects.clear()

    # ------------------------------------------------------------------
    # Thread body
    # ------------------------------------------------------------------

    def run(self):
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.camera_error.emit(
                f"Cannot open camera (index {self.device_index}).\n"
                "Check that a camera is connected and not used by another app."
            )
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._running  = True
        frame_count    = 0

        while self._running:
            ret, frame = cap.read()
            if not ret:
                self.camera_error.emit("Camera read failed — device may have disconnected.")
                break

            frame_count += 1

            # QR scan on every Nth frame only
            if frame_count % _SCAN_EVERY_N_FRAMES == 0:
                codes = self._detect_qr(frame)
                self._current_rects = [c['rect'] for c in codes]

                new = [c for c in codes if c['data'] not in self._seen_codes]
                if new:
                    for c in new:
                        self._seen_codes.add(c['data'])
                    self._enrich_and_emit(new)

            # Draw persisted bounding boxes on every frame
            for rect in self._current_rects:
                cv2.rectangle(
                    frame,
                    (rect.left, rect.top),
                    (rect.left + rect.width, rect.top + rect.height),
                    _ACCENT_BGR, 3
                )

            self.frame_ready.emit(self._to_qimage(frame))
            self.msleep(33)   # ~30 fps

        cap.release()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_qr(self, bgr_frame) -> list:
        rgb   = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        codes = []
        try:
            from core.qr.scanner import scan_image
            codes = scan_image(Image.fromarray(rgb))
        except Exception:
            pass
        for c in codes:
            c['page'] = None
        return codes

    def _enrich_and_emit(self, codes: list):
        """Check safety for new codes, then emit qr_detected."""
        from core.qr.malware_checker import check_url, is_url
        results = []
        for i, c in enumerate(codes, start=1):
            data = c['data']
            safety = (
                check_url(data, self.virustotal_key)
                if is_url(data)
                else {'status': 'unknown', 'source': 'n/a',
                      'detail': 'Not a URL — no safety check performed.'}
            )
            results.append({**c, 'safety': safety, 'index': i})
        self.qr_detected.emit(results)

    @staticmethod
    def _to_qimage(bgr_frame) -> QImage:
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        return img.copy()   # copy so numpy buffer isn't freed before Qt uses it
