import os
import platform
import psutil
import subprocess
import webbrowser
from threading import Thread
from datetime import datetime, timedelta
from colorama import Fore, Style
import time
import sys

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE_DIR = os.path.join(ROOT_DIR, 'workspace')

# Add the root directory to Python path
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

class ProgramManager:
    def __init__(self):
        self.program_paths = {}
        self.running_processes = {}
        self.windows_apps = {
            'explorer': 'explorer.exe',
            'edge': 'msedge.exe',
            'controlpanel': 'control.exe',
            'notepad': 'notepad.exe',
            'calc': 'calc.exe',
            'cmd': 'cmd.exe',
            'taskmgr': 'taskmgr.exe',
            'mspaint': 'mspaint.exe',
            'wordpad': 'wordpad.exe',
            'settings': 'ms-settings:',
            'winver': 'winver.exe',
            'regedit': 'regedit.exe',
            'powershell': 'powershell.exe',
            'terminal': 'wt.exe',
        }
        
        # File type handlers
        self.file_handlers = {
            '.py': {'cmd': 'python', 'args': []},
            '.java': {'cmd': 'javac', 'args': [], 'run_cmd': 'java'},
            '.cpp': {'cmd': 'g++', 'args': ['-o', '{output}']},
            '.c': {'cmd': 'gcc', 'args': ['-o', '{output}']},
            '.bat': {'cmd': 'cmd.exe', 'args': ['/c']},
            '.sh': {'cmd': 'bash', 'args': []},
            '.js': {'cmd': 'node', 'args': []},
            '.html': {'cmd': 'start', 'args': []},  # Opens in default browser
            '.exe': {'cmd': '', 'args': []},  # Direct execution
        }
        
        # Start scanning in background
        Thread(target=self._scan_programs, daemon=True).start()
        # Add chrome specifically for web browsing
        if platform.system() == 'Windows':
            chrome_paths = [
                os.path.join(os.environ.get('ProgramFiles', ''), 'Google/Chrome/Application/chrome.exe'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Google/Chrome/Application/chrome.exe'),
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    self.program_paths['chrome'] = path
                    break

    def _scan_programs(self):
        """Scan and store program paths"""
        if platform.system() == 'Windows':
            self._scan_windows_programs()
        else:
            self._scan_unix_programs()

    def _scan_windows_programs(self):
        """Scan Windows programs"""
        system_dirs = [
            os.environ.get('SystemRoot', ''),
            os.path.join(os.environ.get('SystemRoot', ''), 'System32'),
            os.environ.get('ProgramFiles', ''),
            os.environ.get('ProgramFiles(x86)', ''),
            os.environ.get('LocalAppData', ''),
            os.path.join(os.environ.get('LocalAppData', ''), 'Programs'),
            os.environ.get('AppData', '')
        ]

        # Add Windows default apps
        for app_name, app_exe in self.windows_apps.items():
            for directory in system_dirs:
                if not directory:
                    continue
                app_path = os.path.join(directory, app_exe)
                if os.path.exists(app_path):
                    self.program_paths[app_name] = app_path
                    break

    def _scan_unix_programs(self):
        """Scan Unix programs"""
        unix_dirs = [
            '/usr/bin',
            '/usr/local/bin',
            '/opt',
            '/Applications'
        ]
        
        for directory in unix_dirs:
            if not os.path.exists(directory):
                continue
            
            try:
                for item in os.listdir(directory):
                    full_path = os.path.join(directory, item)
                    if os.access(full_path, os.X_OK):
                        self.program_paths[item.lower()] = full_path
            except (PermissionError, OSError):
                continue

    def open_program(self, program_name):
        """Open a program by name or path"""
        try:
            program_name = program_name.lower()
            
            # Handle workspace files
            if program_name.startswith('workspace '):
                file_name = program_name[10:].strip()
                file_path = os.path.join(WORKSPACE_DIR, file_name)
                if os.path.exists(file_path):
                    return self._handle_file(file_path)
                return f"File '{file_name}' not found in workspace"
            
            # Handle web URLs
            if program_name.startswith(('http://', 'https://', 'www.')):
                if not program_name.startswith(('http://', 'https://')):
                    program_name = 'https://' + program_name
                webbrowser.open(program_name)
                return f"Opening {program_name} in browser"

            # Handle file paths
            if os.path.exists(program_name):
                return self._handle_file(program_name)
            
            # Handle Windows special cases
            if platform.system() == 'Windows':
                if program_name == 'settings':
                    os.system('start ms-settings:')
                    return "Opening Windows Settings"
                elif program_name == 'explorer':
                    os.system('explorer')
                    return "Opening File Explorer"
                elif program_name == 'controlpanel':
                    os.system('control')
                    return "Opening Control Panel"
            
            # Try to find and open the program
            try:
                if program_name in self.program_paths:
                    process = subprocess.Popen([self.program_paths[program_name]])
                    self.running_processes[program_name] = process
                    return f"Started {program_name}"
                
                # Try system commands first
                process = subprocess.Popen([program_name], shell=True)
                self.running_processes[program_name] = process
                return f"Started {program_name}"
            except Exception as e:
                return f"Could not start {program_name}: {str(e)}"
            
        except Exception as e:
            return f"Error handling program: {str(e)}"

    def _handle_file(self, file_path):
        """Handle different file types"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.file_handlers:
            return f"Unsupported file type: {ext}"
            
        handler = self.file_handlers[ext]
        
        try:
            if ext in ['.cpp', '.c']:
                # Compile C/C++ files
                output = file_path.rsplit('.', 1)[0] + '.exe'
                args = [handler['cmd']] + handler['args']
                args = [arg.format(output=output) for arg in args]
                args.append(file_path)
                
                compile_process = subprocess.run(args, capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return f"Compilation error: {compile_process.stderr}"
                
                process = subprocess.Popen([output])
                self.running_processes[os.path.basename(output)] = process
                return f"Compiled and running {os.path.basename(file_path)}"
                
            elif ext == '.java':
                # Compile and run Java files
                compile_process = subprocess.run([handler['cmd'], file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return f"Compilation error: {compile_process.stderr}"
                
                class_file = file_path.rsplit('.', 1)[0]
                process = subprocess.Popen(['java', os.path.basename(class_file)])
                self.running_processes[os.path.basename(class_file)] = process
                return f"Compiled and running {os.path.basename(file_path)}"
                
            elif ext == '.exe':
                # Direct execution for exe files
                process = subprocess.Popen([file_path])
                self.running_processes[os.path.basename(file_path)] = process
                return f"Running {os.path.basename(file_path)}"
                
            else:
                # Handle other file types
                cmd = [handler['cmd']] + handler['args'] + [file_path]
                process = subprocess.Popen(cmd)
                self.running_processes[os.path.basename(file_path)] = process
                return f"Running {os.path.basename(file_path)}"
                
        except Exception as e:
            return f"Error handling file {file_path}: {str(e)}"

    def close_program(self, program_name):
        """Close a running program"""
        program_name = program_name.lower()
        
        # Handle 'close all' command
        if program_name == 'all':
            if not self.running_processes:
                return "No programs running"
            
            closed_programs = []
            failed_programs = []
            
            for prog_name, process in list(self.running_processes.items()):
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    del self.running_processes[prog_name]
                    closed_programs.append(prog_name)
                except Exception:
                    failed_programs.append(prog_name)
            
            response = f"Closed programs: {', '.join(closed_programs)}" if closed_programs else ""
            if failed_programs:
                response += f"\nFailed to close: {', '.join(failed_programs)}"
            return response
        
        if program_name not in self.running_processes:
            return f"Program '{program_name}' is not running"
            
        try:
            process = self.running_processes[program_name]
            process.terminate()
            process.wait(timeout=5)
            del self.running_processes[program_name]
            return f"Closed {program_name}"
        except Exception as e:
            return f"Error closing {program_name}: {str(e)}"

    def list_running_programs(self):
        """List all programs started by the bot"""
        if not self.running_processes:
            return "No programs running"
            
        return "Running programs:\n" + "\n".join(f"- {name}" for name in self.running_processes.keys())

    def list_available_programs(self):
        """List all detected programs"""
        if not self.program_paths:
            return "No programs detected"
            
        response = "Available Programs:\n"
        sorted_programs = sorted(self.program_paths.keys())
        
        current_letter = ''
        for program in sorted_programs:
            first_letter = program[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                response += f"\n{current_letter}:\n"
            response += f"- {program}\n"
            
        return response 

    def get_system_info(self):
        """Get system information in a neofetch-like format"""
        if platform.system() == 'Linux':
            try:
                return subprocess.check_output(['neofetch']).decode()
            except:
                pass
        
        # Get system information
        info = {
            'OS': f"{platform.system()} {platform.release()}",
            'Host': platform.node(),
            'Kernel': platform.version(),
            'Uptime': self._get_uptime(),
            'Shell': os.environ.get('SHELL', os.environ.get('COMSPEC', '')),
            'CPU': platform.processor(),
            'Memory': self._get_memory_info(),
            'Disk': self._get_disk_info(),
        }
        
        # Format the output
        return "\n".join(f"{k}: {v}" for k, v in info.items())

    def _get_uptime(self):
        """Get system uptime"""
        if platform.system() == 'Windows':
            return str(timedelta(seconds=int(time.time() - psutil.boot_time())))
        return ""

    def _get_memory_info(self):
        """Get memory information"""
        mem = psutil.virtual_memory()
        return f"Total: {self._format_bytes(mem.total)} | Used: {self._format_bytes(mem.used)} ({mem.percent}%)"

    def _get_disk_info(self):
        """Get disk information"""
        disk = psutil.disk_usage('/')
        return f"Total: {self._format_bytes(disk.total)} | Used: {self._format_bytes(disk.used)} ({disk.percent}%)"

    def _format_bytes(self, bytes):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024

    def get_window_size(self):
        """Get terminal window size"""
        size = os.get_terminal_size()
        return f"Width: {size.columns}, Height: {size.lines}"

    def set_window_size(self, columns=48, lines=30):
        """Set terminal window size"""
        if platform.system() == 'Windows':
            os.system(f'mode con: cols={columns} lines={lines}')
        else:
            print(f'\x1b[8;{lines};{columns}t')
        return f"Window size set to {columns}x{lines}" 