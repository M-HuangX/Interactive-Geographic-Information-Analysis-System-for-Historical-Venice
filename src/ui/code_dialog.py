# src/ui/code_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPlainTextEdit, 
                           QPushButton, QHBoxLayout, QWidget, QProgressBar)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer

class CodeExecutionDialog(QDialog):
    codeExecuted = pyqtSignal(str, bool)
    
    def __init__(self, code: str, output: str, executor, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.code = code
        self.executor = executor
        self.setup_ui(code, output)
        self.setup_connections()
        
        # Add a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.layout().insertWidget(2, self.progress_bar)  # Insert before the button
    
    def setup_ui(self, code: str, output: str):
        self.setWindowTitle("Code Execution Details")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.WindowType.Window)

        layout = QVBoxLayout(self)
        
        # Code section
        code_label = QLabel("Generated Code:")
        layout.addWidget(code_label)
        
        self.code_display = QPlainTextEdit()
        self.code_display.setPlainText(code)
        self.code_display.setReadOnly(False)
        layout.addWidget(self.code_display)
        
        # Output section
        output_label = QLabel("Execution Output:")
        layout.addWidget(output_label)
        
        self.output_display = QPlainTextEdit()
        self.output_display.setPlainText(output)
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        self.execute_button = QPushButton("Re-execute Code")
        button_layout.addWidget(self.execute_button)
        
        self.close_button = QPushButton("Close")
        button_layout.addWidget(self.close_button)
        
        layout.addWidget(button_container)
    
    def setup_connections(self):
        self.execute_button.clicked.connect(self.execute_code)
        self.close_button.clicked.connect(self.close)
        
        # Connect to the executor signal
        self.executor.execution_finished.connect(self.handle_execution_result)
    
    def execute_code(self):
        current_code = self.code_display.toPlainText()
        
        # Display progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Display busy status
        self.execute_button.setEnabled(False)
        
        # Execute code
        self.executor.execute(current_code)
    
    def handle_execution_result(self, result):
        output, html_content, success = result
        
        # Update output display
        self.output_display.setPlainText(output)
        
        # Hide the progress bar and restore the button state
        self.progress_bar.setVisible(False)
        self.execute_button.setEnabled(True)
        
        # Send execution result signal
        if success and html_content:
            self.codeExecuted.emit(html_content, success)