import sys
import os
import traceback  # Only for error handling, not debug
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QMenu, QSizePolicy, QSystemTrayIcon, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon
import ping3
from settings import Settings
from settings_dialog import SettingsDialog

# Constants
CORNER_MARGIN = 5
POSITIONS = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]

class PingOverlay(QMainWindow):
    """The always-on-top overlay window displaying the current ping."""
    def __init__(self, settings, tray_app=None):
        super().__init__()
        self.settings = settings
        self.tray_app = tray_app  # Reference to tray app for sync
        self.allow_close = False  # Only allow close if explicitly set
        self.setWindowTitle("Ping Overlay")
        self.setup_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ping label setup
        self.ping_label = QLabel("-- ms")
        self.ping_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: rgba(0, 0, 0, 150);
                padding: 3px 8px;
                border-radius: 5px;
            }
        """)
        font = QFont()
        font.setPointSize(10)
        self.ping_label.setFont(font)
        self.ping_label.setMinimumSize(0, 0)
        self.ping_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.setCentralWidget(self.ping_label)
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.adjust_overlay_size()

        # Set initial position
        self.move_to_position(POSITIONS[0])

        # Setup ping timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ping)
        self.timer.start(1000)  # Update every second

        # Make window draggable
        self.old_pos = None

    def setup_window_flags(self):
        """Set up window flags based on click-through setting."""
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        if self.settings.data.get("click_through", False):
            flags |= Qt.WindowType.WindowTransparentForInput
        self.setWindowFlags(flags)

    def update_click_through(self):
        """Update click-through mode when settings change."""
        self.setup_window_flags()
        self.show()  # Re-show to apply new flags

    def adjust_overlay_size(self):
        self.ping_label.adjustSize()
        self.adjustSize()
        self.setFixedSize(self.ping_label.sizeHint())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        # Position submenu
        position_menu = menu.addMenu("Position")
        for pos in POSITIONS:
            action = QAction(pos, self)
            action.triggered.connect(lambda checked, p=pos: self.move_to_position(p))
            position_menu.addAction(action)
        menu.addSeparator()
        # Hide overlay action
        hide_action = QAction("Hide Overlay", self)
        hide_action.triggered.connect(self.hide_overlay_from_menu)
        menu.addAction(hide_action)
        menu.exec(event.globalPos())

    def hide_overlay_from_menu(self):
        if self.tray_app:
            self.tray_app.hide_overlay()
        else:
            self.hide()

    def move_to_position(self, position):
        self.adjust_overlay_size()
        screen = QApplication.primaryScreen().geometry()
        if position == "Top Left":
            self.move(CORNER_MARGIN, CORNER_MARGIN)
        elif position == "Top Right":
            self.move(screen.width() - self.width() - CORNER_MARGIN, CORNER_MARGIN)
        elif position == "Bottom Left":
            self.move(CORNER_MARGIN, screen.height() - self.height() - CORNER_MARGIN)
        elif position == "Bottom Right":
            self.move(screen.width() - self.width() - CORNER_MARGIN, screen.height() - self.height() - CORNER_MARGIN)

    def update_ping(self):
        host = self.settings.data.get("host", "google.com")
        try:
            ping_time = ping3.ping(host)
            if ping_time is not None and ping_time > 0:
                ping_time_ms = ping_time * 1000
                self.ping_label.setText(f"{ping_time_ms:.0f} ms")
                # Use thresholds from settings
                green = self.settings.data.get("green_threshold", 50)
                yellow = self.settings.data.get("yellow_threshold", 100)
                if ping_time_ms < green:
                    color = "#00ff00"  # Green
                elif ping_time_ms < yellow:
                    color = "#ffff00"  # Yellow
                else:
                    color = "#ff0000"  # Red
                self.ping_label.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        background-color: rgba(0, 0, 0, 150);
                        padding: 3px 8px;
                        border-radius: 5px;
                    }}
                """)
            else:
                self.ping_label.setText("Timeout")
                self.ping_label.setStyleSheet("""
                    QLabel {
                        color: #ff0000;
                        background-color: rgba(0, 0, 0, 150);
                        padding: 3px 8px;
                        border-radius: 5px;
                    }
                """)
        except Exception:
            self.ping_label.setText("Error")
            self.ping_label.setStyleSheet("""
                QLabel {
                    color: #ff0000;
                    background-color: rgba(0, 0, 0, 150);
                    padding: 3px 8px;
                    border-radius: 5px;
                }
            """)
        self.adjust_overlay_size()

    def closeEvent(self, event):
        """Only allow closing if allow_close is True, otherwise just hide."""
        if self.allow_close:
            event.accept()
        else:
            event.ignore()
            if self.tray_app:
                self.tray_app.hide_overlay(from_overlay=True)
            else:
                self.hide()

class TrayApp:
    """Manages the system tray icon, menu, and overlay window."""
    def __init__(self, app, settings):
        self.app = app
        self.settings = settings
        self.overlay = PingOverlay(settings, tray_app=self)
        self.tray = QSystemTrayIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icon.ico')))
        self.tray.setToolTip('Ping Overlay')
        self.menu = QMenu()

        # Tray menu actions
        self.show_overlay_action = QAction('Show Overlay')
        self.show_overlay_action.setCheckable(True)
        self.show_overlay_action.setChecked(True)
        self.menu.addAction(self.show_overlay_action)
        self.menu.addSeparator()
        
        # Click-through toggle
        self.click_through_action = QAction('Click-Through Mode')
        self.click_through_action.setCheckable(True)
        self.click_through_action.setChecked(self.settings.data.get("click_through", False))
        self.menu.addAction(self.click_through_action)
        self.menu.addSeparator()
        
        self.settings_action = QAction('Open Settings')
        self.menu.addAction(self.settings_action)
        self.menu.addSeparator()
        self.exit_action = QAction('Exit')
        self.menu.addAction(self.exit_action)
        self.tray.setContextMenu(self.menu)
        self.tray.show()

        # Connect tray actions
        self.show_overlay_action.toggled.connect(self.toggle_overlay)
        self.click_through_action.toggled.connect(self.toggle_click_through)
        self.settings_action.triggered.connect(self.open_settings)
        self.exit_action.triggered.connect(self.exit_app)
        self.tray.activated.connect(self.on_tray_activated)
        self.recreating_overlay = False

    def show_overlay(self):
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()
        self.show_overlay_action.setChecked(True)

    def hide_overlay(self):
        self.overlay.hide()
        self.show_overlay_action.setChecked(False)

    def toggle_overlay(self, checked):
        if checked:
            self.show_overlay()
        else:
            self.hide_overlay()

    def toggle_click_through(self, checked):
        """Toggle click-through mode for the overlay."""
        self.settings.data["click_through"] = checked
        self.settings.save()
        self.overlay.update_click_through()

    def open_settings(self):
        dlg = SettingsDialog(self.settings, parent=None, first_run=False)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            # Clean up old overlay
            self.recreating_overlay = True
            self.overlay.allow_close = True
            self.overlay.close()
            self.overlay.deleteLater()
            self.recreating_overlay = False
            self.overlay = PingOverlay(self.settings, tray_app=self)
            # Update click-through state in tray menu
            self.click_through_action.setChecked(self.settings.data.get("click_through", False))
            # Always show overlay after saving settings
            self.show_overlay()
        # If canceled, do nothing

    def exit_app(self):
        self.tray.hide()
        self.overlay.allow_close = True
        self.overlay.close()
        self.app.quit()
        os._exit(0)  # Ensure full exit

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_settings()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set global application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    app.setQuitOnLastWindowClosed(False)
    settings = Settings()

    # Show settings dialog on startup if enabled
    show_overlay = True
    if settings.data.get("show_settings_on_startup", True):
        dlg = SettingsDialog(settings, first_run=True)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

    tray_app = TrayApp(app, settings)
    if show_overlay:
        tray_app.show_overlay()
    else:
        tray_app.hide_overlay()
    sys.exit(app.exec()) 