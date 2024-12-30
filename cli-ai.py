import os
import sys
from PyQt6.QtWidgets import QApplication
from src.commands.program_manager import ProgramManager
from src.commands.file_operations import FileOperations
from src.gui.main_window import SidebarWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Initialize managers
    program_manager = ProgramManager()
    file_ops = FileOperations()
    
    # Create and show window
    window = SidebarWindow(program_manager, file_ops)
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()