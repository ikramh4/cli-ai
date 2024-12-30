import os
from datetime import datetime
import sys

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_DIR = os.path.join(ROOT_DIR, 'workspace')

# Add the root directory to Python path
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

class FileOperations:
    def __init__(self):
        # Create workspace directory if it doesn't exist
        if not os.path.exists(WORKSPACE_DIR):
            os.makedirs(WORKSPACE_DIR)

    def create_file(self, filename, content=''):
        """Create a file in the workspace directory with specified content"""
        try:
            file_path = os.path.join(WORKSPACE_DIR, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            return f"File '{filename}' created successfully in workspace"
        except Exception as e:
            return f"Error creating file: {str(e)}"

    def list_files(self):
        """List all files in the workspace directory with details"""
        try:
            files = os.listdir(WORKSPACE_DIR)
            if not files:
                return "Workspace is empty"
            
            response = "Workspace files:\n"
            response += f"Location: {WORKSPACE_DIR}\n\n"
            
            for file in sorted(files):
                file_path = os.path.join(WORKSPACE_DIR, file)
                stats = os.stat(file_path)
                size = self._format_size(stats.st_size)
                modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                response += f"- {file}\n"
                response += f"  Size: {size} | Modified: {modified}\n"
            
            return response
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _format_size(self, size):
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024 