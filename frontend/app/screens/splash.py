from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

from frontend.app.core.display import detect_display_profile


class SplashScreen(QWidget):
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._progress_value = 0
        self.setWindowTitle("PRO CORE")
        profile = detect_display_profile()
        self.setFixedSize(round(520 * profile.ui_scale), round(280 * profile.ui_scale))
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setObjectName("splash")

        title = QLabel("PRO CORE")
        title.setObjectName("splashTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Assistencia tecnica")
        subtitle.setObjectName("splashSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        layout = QVBoxLayout(self)
        margin = round(24 * profile.ui_scale)
        layout.setContentsMargins(margin, margin, margin, round(18 * profile.ui_scale))
        layout.setSpacing(round(8 * profile.ui_scale))
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(self.progress)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)

    def start(self) -> None:
        self._center_on_screen()
        self.show()
        self.timer.start(18)

    def _advance(self) -> None:
        self._progress_value += 2
        self.progress.setValue(self._progress_value)

        if self._progress_value >= 100:
            self.timer.stop()
            self.finished.emit()

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return

        geometry = screen.availableGeometry()
        self.move(geometry.center() - self.rect().center())
