# src/ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt
from ..ui.chat_panel import ChatPanel
from ..ui.map_panel import MapPanel
from ..ui.code_dialog import CodeExecutionDialog
from ..core.chat_manager import ChatManager
from ..core.code_executor import CodeExecutor
from ..utils.code_parser import CodeParser
import traceback
import logging
from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication

class MainWindow(QMainWindow):
    def __init__(self, config: dict, prompts: dict):
        super().__init__()
        self.config = config
        self.prompts = prompts
        
        # Add log configuration
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        self.chat_manager = ChatManager(
            api_key=config['api_key'],
            model=config['model']
        )
        self.code_executor = CodeExecutor()
        self.code_parser = CodeParser()
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        self.setWindowTitle("Interactive Geography Analysis")
        self.setGeometry(100, 100, 
                        self.config['ui']['window_size']['width'],
                        self.config['ui']['window_size']['height'])
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create panels
        self.chat_panel = ChatPanel()
        self.map_panel = MapPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.chat_panel)
        splitter.addWidget(self.map_panel)
        
        # Set size ratio
        total_width = sum(self.config['ui']['split_ratio'])
        sizes = [
            size * self.config['ui']['window_size']['width'] // total_width 
            for size in self.config['ui']['split_ratio']
        ]
        splitter.setSizes(sizes)
        
        layout.addWidget(splitter)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Create a status indicator
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                color: #666;
            }
        """)
        self.statusBar.addWidget(self.status_label)
        
        # Set the default state
        self.update_status("Ready")
        
    def update_status(self, status: str):
        """Update status bar display"""
        self.status_label.setText(status)
    
    def setup_connections(self):
        self.chat_panel.send_button.clicked.connect(self.handle_user_input)
    
    def handle_user_input(self):
        user_message = self.chat_panel.user_input.toPlainText().strip()
        if not user_message:
            return
            
        try:
            # Clear the input box first
            self.chat_panel.user_input.clear()
            
            # Update the status immediately and add the user message
            self.update_status("AI Agent is thinking...")
            self.chat_panel.add_message(user_message, is_user=True)
            self.chat_manager.add_message(user_message, is_user=True)
            
            # Force processing of all pending UI events
            QApplication.processEvents()
            
            # Get AI response
            self.logger.debug("Requesting AI response...")
            response = self.chat_manager.get_response(self.prompts['system_prompt'])
            
            if response:
                # Update Status
                self.logger.debug("AI response received")
                self.update_status("Executing visualization code...")
                
                # Add AI response to chat log
                self.chat_panel.add_message(response, is_user=False)
                self.chat_manager.add_message(response, is_user=False)
                
                # Extract code
                code = self.code_parser.extract_python_code(response)
                self.logger.debug("Extracted code: %s", code)
                
                if code:
                    # Initialize and display the code execution dialog box
                    self.logger.debug("Initializing code execution dialog")
                    dialog = CodeExecutionDialog(
                        code=code,
                        output="Executing...",
                        executor=self.code_executor,
                        parent=self
                    )
                    dialog.codeExecuted.connect(self.handle_code_execution)
                    dialog.show()
                    
                    # Execute code
                    self.logger.debug("Starting code execution")
                    self.code_executor.execute(code)
                else:
                    self.logger.warning("No code found in AI response")
                    self.update_status("No code to execute")
            
        except Exception as e:
            self.logger.error("Error in handle_user_input: %s", str(e))
            self.logger.error("Traceback: %s", traceback.format_exc())
            self.update_status("Error occurred")
            QMessageBox.critical(
                self,
                "Error",
                f"{self.prompts['error_messages']['api_error']}\n{str(e)}"
            )
    
    def handle_code_execution(self, html_path: str, success: bool):
        """Processing code execution results"""
        self.logger.debug(f"Code execution result - Success: {success}")
        if success and html_path:
            self.logger.debug(f"Updating map with file: {html_path}")
            self.map_panel.update_map(html_path)
            self.update_status("Visualization complete")
        else:
            self.logger.debug("Code execution failed or no HTML generated")
            self.update_status("Execution failed")