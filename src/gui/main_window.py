import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QTextEdit, QPushButton, QScrollArea, QWIDGETSIZE_MAX)
from PyQt6.QtCore import Qt, QSize, QTimer, QPoint
from PyQt6.QtGui import QFont, QIcon, QColor
from qt_material import apply_stylesheet
from .settings_dialog import SettingsDialog

class SidebarWindow(QMainWindow):
    def __init__(self, program_manager, file_ops):
        super().__init__()
        self.program_manager = program_manager
        self.file_ops = file_ops
        self.setWindowTitle("CLI Bot - by: H4INCE")
        
        # Load settings first
        self.settings = SettingsDialog.load_settings()
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nh.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Apply theme from settings
        theme = self.settings.get('theme', 'Dark Theme')
        if theme == "Dark Theme":
            apply_stylesheet(self, theme='dark_blue.xml')
        else:
            apply_stylesheet(self, theme='light_blue.xml')
        
        # Initialize window states
        self.is_sidebar = False
        self.always_on_top = False
        self.last_normal_geometry = None
        
        # Set initial size and minimum size
        self.resize(600, 400)
        self.setMinimumSize(400, 300)  # Set minimum window size
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)
        
        # Left side buttons
        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # Add mode buttons to left side
        self.normal_button = QPushButton("Normal")
        self.sidebar_button = QPushButton("Sidebar")
        
        for btn in [self.normal_button, self.sidebar_button]:
            btn.setFixedHeight(30)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #444444;
                    border-radius: 15px;
                    padding: 5px 15px;
                    color: #888888;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:checked {
                    background-color: #0078d4;
                    border-color: #0078d4;
                    color: white;
                }
            """)
        
        self.normal_button.setChecked(True)
        self.normal_button.clicked.connect(self.toggle_mode)
        self.sidebar_button.clicked.connect(self.toggle_mode)
        
        # Add pin button
        self.pin_button = QPushButton("Pin")
        self.pin_button.setFixedHeight(30)
        self.pin_button.setCheckable(True)
        self.pin_button.setStyleSheet(self.normal_button.styleSheet())
        self.pin_button.clicked.connect(self.toggle_always_on_top)
        
        # Add buttons to left layout
        left_layout.addWidget(self.normal_button)
        left_layout.addWidget(self.sidebar_button)
        left_layout.addWidget(self.pin_button)
        
        # Right side buttons
        right_buttons = QWidget()
        right_layout = QHBoxLayout(right_buttons)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Add settings button to right side
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedHeight(30)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #444444;
                border-radius: 15px;
                padding: 5px 15px;
                color: #888888;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.settings_button.clicked.connect(self.show_settings)
        right_layout.addWidget(self.settings_button)
        
        # Add left and right button groups to main button layout
        button_layout.addWidget(left_buttons)
        button_layout.addStretch()
        button_layout.addWidget(right_buttons)
        
        # Add output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
            }
        """)
        
        # Add command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.execute_command)
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                color: #333333;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
                background-color: #f5f5f5;
            }
        """)
        
        # Add elements to layout
        layout.addWidget(button_bar)
        layout.addWidget(self.output_area)
        layout.addWidget(self.command_input)
        
        # Initialize loading animation
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading)
        self.loading_dots = 0
        self.loading_text = ""
        self.loading_color = ""
        
        # Show welcome message with animation
        self.display_output("Welcome to CLI Bot! Type 'help' for commands.", animate=True)
        
        # Set focus to command input
        self.command_input.setFocus()

    def toggle_mode(self):
        sender = self.sender()
        if sender == self.normal_button and self.normal_button.isChecked():
            self.sidebar_button.setChecked(False)
            self.to_normal_mode()
        elif sender == self.sidebar_button and self.sidebar_button.isChecked():
            self.normal_button.setChecked(False)
            self.to_sidebar_mode()
        else:
            # Ensure one mode is always selected
            if not self.normal_button.isChecked() and not self.sidebar_button.isChecked():
                sender.setChecked(True)

    def to_normal_mode(self):
        if self.is_sidebar:
            self.is_sidebar = False
            self.setFixedSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)  # Allow resizing in both directions
            if self.last_normal_geometry:
                self.setGeometry(self.last_normal_geometry)
            else:
                self.resize(600, 400)  # Default size if no previous geometry

    def to_sidebar_mode(self):
        if not self.is_sidebar:
            self.last_normal_geometry = self.geometry()
            self.is_sidebar = True
            screen = self.screen().size()
            self.setFixedSize(400, screen.height())  # Fix both width and height
            self.move(screen.width() - 400, 0)

    def execute_command(self):
        command = self.command_input.text().strip()
        self.command_input.clear()
        
        if not command:
            return
            
        # Display user command with custom color
        self.output_area.append(
            f'<span style="color: {self.settings.get("user_color", "#00ff00")}">You:</span> {command}'
        )
        
        if command.lower() == 'exit':
            self.close()
            return
            
        # Process commands
        if command.lower() == 'help':
            response = """Available Commands:

<b>System Commands</b>
    <span style="color: #00ff00;">system info</span>
        Show detailed system information
    <span style="color: #00ff00;">clear</span>
        Clear the output area
    <span style="color: #00ff00;">exit</span>
        Close the application

<b>Program Management</b>
    <span style="color: #00ff00;">open</span> &lt;program/url&gt;
        Open a program, file, or website
        Examples: 
        - open notepad
        - open chrome
        - open www.google.com
        - open C:/path/to/file.exe

    <span style="color: #00ff00;">close</span> &lt;program&gt;
        Close a specific running program
    
    <span style="color: #00ff00;">close all</span>
        Close all running programs
    
    <span style="color: #00ff00;">list programs</span>
        Show all available programs
    
    <span style="color: #00ff00;">running programs</span>
        Show currently running programs

<b>File Operations</b>
    <span style="color: #00ff00;">create file</span> &lt;filename&gt; &lt;content&gt;
        Create a new file in workspace
        Example: create file test.txt Hello World
    
    <span style="color: #00ff00;">list files</span>
        Show all files in workspace
    
    <span style="color: #00ff00;">open workspace</span> &lt;filename&gt;
        Open a file from workspace
        Example: open workspace script.py

<b>Window Controls</b>
    <span style="color: #00ff00;">Normal/Sidebar</span>
        Toggle between window modes
    
    <span style="color: #00ff00;">Pin</span>
        Toggle always-on-top mode"""
            self.display_output(response, animate=False, color='#ffffff')
        elif command.lower() == 'clear':
            self.output_area.clear()
            self.display_output("Output cleared!", animate=True)
        else:
            # Handle other commands
            if command.lower().startswith('open '):
                response = self.program_manager.open_program(command[5:])
            elif command.lower().startswith('close '):
                response = self.program_manager.close_program(command[6:])
            elif command.lower() == 'list programs':
                response = self.program_manager.list_available_programs()
            elif command.lower() == 'running programs':
                response = self.program_manager.list_running_programs()
            elif command.lower() == 'system info':
                response = self.program_manager.get_system_info()
            elif command.lower().startswith('create file'):
                parts = command.split(maxsplit=3)
                if len(parts) < 4:
                    response = "Usage: create file <filename> <content>"
                else:
                    _, _, filename, content = parts
                    response = self.file_ops.create_file(filename, content)
            elif command.lower() == 'list files':
                response = self.file_ops.list_files()
            else:
                response = f"Unknown command. Type 'help' for available commands."
            
            self.display_output(response, animate=True, color='#00ffff')
        
    def display_output(self, text, animate=True, color='#ffffff'):
        if not animate:
            formatted_text = text.replace('\n', '<br>')
            self.output_area.append(
                f'<span style="color: {self.settings.get("bot_color", "#ff00ff")}">'
                f'{self.settings.get("bot_prefix", "Bot:")}</span> '
                f'<span style="color: {color};">{formatted_text}</span>'
            )
            return
        
        # Start loading animation
        self.loading_text = text
        self.loading_color = color
        self.loading_dots = 0
        self.output_area.append(
            f'<span style="color: {self.settings.get("bot_color", "#ff00ff")}">'
            f'{self.settings.get("bot_prefix", "Bot:")}</span> '
            f'<span style="color: {color};">Loading</span>'
        )
        self.loading_timer.start(500)  # Update every 500ms

    def update_loading(self):
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        
        # Update the last line
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        
        if self.loading_dots == 0:  # Animation complete
            self.loading_timer.stop()
            # Show final text
            formatted_text = self.loading_text.replace('\n', '<br>')
            cursor.insertHtml(
                f'<span style="color: {self.settings.get("bot_color", "#ff00ff")}">'
                f'{self.settings.get("bot_prefix", "Bot:")}</span> '
                f'<span style="color: {self.loading_color};">{formatted_text}</span>'
            )
        else:
            # Show loading animation
            cursor.insertHtml(
                f'<span style="color: {self.settings.get("bot_color", "#ff00ff")}">'
                f'{self.settings.get("bot_prefix", "Bot:")}</span> '
                f'<span style="color: {self.loading_color};">Loading{dots}</span>'
            )

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        flags = self.windowFlags()
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            self.pin_button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1084d9;
                }
            """)
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.pin_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    color: #888888;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
        self.setWindowFlags(flags)
        self.show() 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self.is_sidebar:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept() 

    def show(self):
        """Override show method to ensure input focus"""
        super().show()
        # Set focus to command input after window is shown
        self.command_input.setFocus()

    def showEvent(self, event):
        """Handle show event to ensure input focus"""
        super().showEvent(event)
        # Set focus to command input after window is shown
        self.command_input.setFocus() 

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def apply_settings(self, settings):
        self.settings = settings
        theme = settings.get('theme', 'Dark Theme')
        if theme == "Dark Theme":
            apply_stylesheet(self, theme='dark_blue.xml')
            # Apply dark theme to input
            self.command_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 2px solid #444444;
                    border-radius: 8px;
                    padding: 10px;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                    background-color: #363636;
                }
            """)
        else:
            apply_stylesheet(self, theme='light_blue.xml')
            # Apply light theme to input
            self.command_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    padding: 10px;
                    color: #333333;
                    font-weight: bold;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                    background-color: #f5f5f5;
                }
            """)
 