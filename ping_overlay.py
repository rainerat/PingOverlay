import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont
import ping3

# Define the margin from the screen corners (in pixels)
CORNER_MARGIN = 5

class PingOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ping Overlay")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create ping label only
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
        self.move_to_position("Top Left")
        
        # Setup ping timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ping)
        self.timer.start(1000)  # Update every second
        
        # Make window draggable
        self.old_pos = None
        
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
        
        # Create Position submenu
        position_menu = menu.addMenu("Position")
        positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
        for pos in positions:
            action = QAction(pos, self)
            action.triggered.connect(lambda checked, p=pos: self.move_to_position(p))
            position_menu.addAction(action)
            
        menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())
        
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
        try:
            ping_time = ping3.ping('google.com') * 1000  # Convert to milliseconds
            if ping_time is not None:
                self.ping_label.setText(f"{ping_time:.0f} ms")
                # Change color based on ping
                if ping_time < 50:
                    color = "#00ff00"  # Green
                elif ping_time < 100:
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
        except Exception as e:
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PingOverlay()
    window.show()
    sys.exit(app.exec()) 