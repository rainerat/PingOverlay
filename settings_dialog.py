from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
import os
import sys

DEFAULT_HOST = "google.com"

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None, first_run=False):
        super().__init__(parent)
        self.setWindowTitle("Ping Overlay Settings")
        # Set custom window icon
        if getattr(sys, 'frozen', False):
            # Running as executable
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            # Running as script
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.settings = settings
        self.setModal(True)
        self.setMinimumWidth(300)
        self.first_run = first_run

        layout = QVBoxLayout()

        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Ping Host:")
        self.host_input = QLineEdit(self.settings.data.get("host", DEFAULT_HOST))
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        layout.addLayout(host_layout)

        # Green threshold
        green_layout = QHBoxLayout()
        green_label = QLabel("Green < ms:")
        self.green_input = QSpinBox()
        self.green_input.setRange(1, 10000)
        self.green_input.setValue(self.settings.data.get("green_threshold", 50))
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_input)
        layout.addLayout(green_layout)

        # Yellow threshold
        yellow_layout = QHBoxLayout()
        yellow_label = QLabel("Yellow < ms:")
        self.yellow_input = QSpinBox()
        self.yellow_input.setRange(1, 10000)
        self.yellow_input.setValue(self.settings.data.get("yellow_threshold", 100))
        yellow_layout.addWidget(yellow_label)
        yellow_layout.addWidget(self.yellow_input)
        layout.addLayout(yellow_layout)

        # Show on startup
        self.show_on_startup_checkbox = QCheckBox("Show this settings dialog on startup")
        self.show_on_startup_checkbox.setChecked(self.settings.data.get("show_settings_on_startup", True))
        layout.addWidget(self.show_on_startup_checkbox)

        # Click through mode
        self.click_through_checkbox = QCheckBox("Enable click-through mode (transparent to mouse clicks)")
        self.click_through_checkbox.setChecked(self.settings.data.get("click_through", False))
        layout.addWidget(self.click_through_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        # Dynamic label for main button
        main_button_label = "Start Overlay" if self.first_run else "Apply Changes"
        self.save_button = QPushButton(main_button_label)
        self.cancel_button = QPushButton("Cancel")
        self.reset_button = QPushButton("Reset to Defaults")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button.clicked.connect(self.reset_defaults)

    def save(self):
        green = self.green_input.value()
        yellow = self.yellow_input.value()
        if green >= yellow:
            QMessageBox.warning(self, "Invalid Thresholds", "Green threshold must be less than yellow threshold.")
            return
        self.settings.data["host"] = self.host_input.text().strip() or DEFAULT_HOST
        self.settings.data["green_threshold"] = green
        self.settings.data["yellow_threshold"] = yellow
        self.settings.data["show_settings_on_startup"] = self.show_on_startup_checkbox.isChecked()
        self.settings.data["click_through"] = self.click_through_checkbox.isChecked()
        self.settings.save()
        self.accept()

    def reset_defaults(self):
        self.host_input.setText(DEFAULT_HOST)
        self.green_input.setValue(50)
        self.yellow_input.setValue(100)
        self.show_on_startup_checkbox.setChecked(True)
        self.click_through_checkbox.setChecked(False)