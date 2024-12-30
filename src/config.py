import os

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(ROOT_DIR, 'workspace')

# Create workspace directory if it doesn't exist
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# Color configurations
COLORS = {
    'PRIMARY': '\033[36m',  # Cyan
    'SUCCESS': '\033[32m',  # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'RESET': '\033[0m'      # Reset
} 