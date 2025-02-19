# src/core/code_executor.py
import os
import glob
from datetime import datetime, timedelta
import logging
from IPython.core.interactiveshell import InteractiveShell
from typing import Tuple
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import sys


class CodeExecutionWorker(QObject):
    finished = pyqtSignal(tuple)
    
    def __init__(self, code: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.code = code
        
        # Make sure the output directory exists
        self.map_dir = './map_output'
        os.makedirs(self.map_dir, exist_ok=True)
        
        # Create a shell instance using the main program's module cache
        self.shell = InteractiveShell.instance()
        if self.shell is None:
            self.shell = InteractiveShell()
        
        # Make sure the shell uses the main program's sys.modules
        self.shell.user_ns.update({
            name: module for name, module in sys.modules.items()
            if not name.startswith('_')
        })
    
    def execute(self):
        output = io.StringIO()
        html_path = None
        success = False
        
        try:
            # Record execution start time
            start_time = datetime.now()
            
            # Execute code
            with redirect_stdout(output), redirect_stderr(output):
                result = self.shell.run_cell(self.code)
                
                if result.success:
                    self.logger.debug("Code execution successful")
                    # Find the latest generated map file
                    html_path = self.find_latest_map(start_time)
                    success = bool(html_path)
                    
                    if success:
                        self.logger.debug(f"Found map file: {html_path}")
                    else:
                        self.logger.warning("No map file found")
                else:
                    self.logger.error("Code execution failed")
                    
        except Exception as e:
            self.logger.error(f"Error during code execution: {str(e)}")
            output.write(f"Error: {str(e)}\n")
            output.write(traceback.format_exc())
            success = False
        
        self.finished.emit((output.getvalue(), html_path, success))
    
    def find_latest_map(self, start_time: datetime) -> str:
        """Find the latest generated map file"""
        pattern = os.path.join(self.map_dir, 'temp_map_*.html')
        try:
            # Get all matching files
            files = glob.glob(pattern)
            if not files:
                return None
            
            # Sort by modification time
            latest_file = max(files, key=os.path.getmtime)
            
            # Check if the file was created during code execution
            file_mtime = datetime.fromtimestamp(os.path.getmtime(latest_file))
            if file_mtime >= start_time:
                return latest_file
                
        except Exception as e:
            self.logger.error(f"Error finding map file: {str(e)}")
        
        return None


class CodeExecutor(QObject):
    execution_finished = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.thread = None
        self.worker = None
    
    def execute(self, code: str) -> None:
        self.logger.debug("Starting code execution")
        
        # If there is a thread running, stop it first
        if self.thread and self.thread.isRunning():
            self.logger.debug("Stopping existing thread")
            self.thread.quit()
            self.thread.wait()
        
        # Create new threads and workers
        self.thread = QThread()
        self.worker = CodeExecutionWorker(code)
        self.worker.moveToThread(self.thread)
        
        # Connecting signals
        self.thread.started.connect(self.worker.execute)
        self.worker.finished.connect(self.handle_execution_result)
        self.worker.finished.connect(self.thread.quit)
        
        # Start the thread
        self.logger.debug("Starting execution thread")
        self.thread.start()
    
    def handle_execution_result(self, result: Tuple[str, str, bool]):
        self.logger.debug("Execution completed - Success: %s, HTML length: %s",
                         result[2], len(result[1]) if result[1] else 0)
        self.execution_finished.emit(result)