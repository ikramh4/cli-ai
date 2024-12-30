from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QColorDialog, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qt_material import apply_stylesheet
import json
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Apply theme based on current settings
        theme = self.settings.get('theme', 'Dark Theme')
        if theme == "Dark Theme":
            # Apply dark theme styles
            self.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-weight: bold;
                }
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #555;
                    border-radius: 3px;
                    background-color: #363636;
                    color: white;
                }
                QPushButton {
                    padding: 5px 15px;
                    border: 1px solid #555;
                    border-radius: 3px;
                    background-color: #363636;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #404040;
                    border-color: #0078d4;
                }
                QComboBox {
                    padding: 5px;
                    border: 1px solid #555;
                    border-radius: 3px;
                    background-color: #363636;
                    color: white;
                }
                QComboBox:hover {
                    border-color: #0078d4;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        else:
            # Apply light theme styles
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                    font-weight: bold;
                }
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: white;
                    color: #333333;
                }
                QPushButton {
                    padding: 5px 15px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: white;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #0078d4;
                }
                QComboBox {
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: white;
                    color: #333333;
                }
                QComboBox:hover {
                    border-color: #0078d4;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Bot Prefix Section
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("Bot Prefix:")
        self.prefix_input = QLineEdit(self.settings.get('bot_prefix', 'Bot:'))
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_input)
        layout.addLayout(prefix_layout)
        
        # Bot Color Section
        bot_color_layout = QHBoxLayout()
        bot_color_label = QLabel("Bot Color:")
        self.bot_color_btn = QPushButton()
        self.bot_color_btn.setFixedSize(50, 25)
        self.bot_color = QColor(self.settings.get('bot_color', '#ff00ff'))
        self.bot_color_btn.setStyleSheet(f"background-color: {self.bot_color.name()}")
        self.bot_color_btn.clicked.connect(self.choose_bot_color)
        bot_color_layout.addWidget(bot_color_label)
        bot_color_layout.addWidget(self.bot_color_btn)
        layout.addLayout(bot_color_layout)
        
        # User Color Section
        user_color_layout = QHBoxLayout()
        user_color_label = QLabel("User Color:")
        self.user_color_btn = QPushButton()
        self.user_color_btn.setFixedSize(50, 25)
        self.user_color = QColor(self.settings.get('user_color', '#00ff00'))
        self.user_color_btn.setStyleSheet(f"background-color: {self.user_color.name()}")
        self.user_color_btn.clicked.connect(self.choose_user_color)
        user_color_layout.addWidget(user_color_label)
        user_color_layout.addWidget(self.user_color_btn)
        layout.addLayout(user_color_layout)
        
        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme"])
        self.theme_combo.setCurrentText(self.settings.get('theme', 'Dark Theme'))
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Update button styles
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1084d9;
            }
        """)
        
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #0078d4;
            }
        """)

    def choose_bot_color(self):
        color = QColorDialog.getColor(self.bot_color, self)
        if color.isValid():
            self.bot_color = color
            self.bot_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def choose_user_color(self):
        color = QColorDialog.getColor(self.user_color, self)
        if color.isValid():
            self.user_color = color
            self.user_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def theme_changed(self, theme):
        if self.parent:
            if theme == "Dark Theme":
                apply_stylesheet(self.parent, theme='dark_blue.xml')
                # Apply dark theme to settings dialog
                self.setStyleSheet("""
                    QDialog {
                        background-color: #2d2d2d;
                        color: white;
                    }
                    QLabel {
                        color: white;
                        font-weight: bold;
                    }
                    QLineEdit {
                        padding: 5px;
                        border: 1px solid #555;
                        border-radius: 3px;
                        background-color: #363636;
                        color: white;
                    }
                    QPushButton {
                        padding: 5px 15px;
                        border: 1px solid #555;
                        border-radius: 3px;
                        background-color: #363636;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                        border-color: #0078d4;
                    }
                    QComboBox {
                        padding: 5px;
                        border: 1px solid #555;
                        border-radius: 3px;
                        background-color: #363636;
                        color: white;
                    }
                    QComboBox:hover {
                        border-color: #0078d4;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border: none;
                    }
                """)
            else:
                apply_stylesheet(self.parent, theme='light_blue.xml')
                # Apply light theme to settings dialog
                self.setStyleSheet("""
                    QDialog {
                        background-color: white;
                        color: #333333;
                    }
                    QLabel {
                        color: #333333;
                        font-weight: bold;
                    }
                    QLineEdit {
                        padding: 5px;
                        border: 1px solid #cccccc;
                        border-radius: 3px;
                        background-color: white;
                        color: #333333;
                    }
                    QPushButton {
                        padding: 5px 15px;
                        border: 1px solid #cccccc;
                        border-radius: 3px;
                        background-color: white;
                        color: #333333;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                        border-color: #0078d4;
                    }
                    QComboBox {
                        padding: 5px;
                        border: 1px solid #cccccc;
                        border-radius: 3px;
                        background-color: white;
                        color: #333333;
                    }
                    QComboBox:hover {
                        border-color: #0078d4;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border: none;
                    }
                """)

    def save_settings(self):
        settings = {
            'bot_prefix': self.prefix_input.text(),
            'bot_color': self.bot_color.name(),
            'user_color': self.user_color.name(),
            'theme': self.theme_combo.currentText()
        }
        
        self.save_to_file(settings)
        if self.parent:
            self.parent.apply_settings(settings)
        self.accept()

    @staticmethod
    def load_settings():
        try:
            settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @staticmethod
    def save_to_file(settings):
        try:
            settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception:
            pass 