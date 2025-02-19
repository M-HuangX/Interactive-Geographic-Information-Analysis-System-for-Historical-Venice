# src/ui/chat_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QTextEdit, 
                          QPushButton, QScrollBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QTextCursor
import html

class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Chat history display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # User input area
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.setMaximumHeight(100)
        self.user_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
        """)
        layout.addWidget(self.user_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0084ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0073e6;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        layout.addWidget(self.send_button)

    def add_message(self, message: str, is_user: bool):
        # Escaping HTML special characters
        escaped_message = html.escape(message)
        # Replace line breaks with HTML line break tags
        formatted_message = escaped_message.replace('\n', '<br>')
        
        # Use table layout to achieve message alignment
        if is_user:
            html_message = f"""
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="right">
                            <table bgcolor="#DCF8C6" style="border-radius: 10px; margin: 5px 0;">
                                <tr>
                                    <td style="padding: 8px;">
                                        <font color="#666666" size="2">You</font><br>
                                        <font color="#000000">{formatted_message}</font>
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td width="10"></td>
                    </tr>
                </table>
            """
        else:
            html_message = f"""
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="10"></td>
                        <td align="left">
                            <table bgcolor="#E8E8E8" style="border-radius: 10px; margin: 5px 0;">
                                <tr>
                                    <td style="padding: 8px;">
                                        <font color="#666666" size="2">Assistant</font><br>
                                        <font color="#000000">{formatted_message}</font>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            """
        
        # Add a message to the display area
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.insertHtml(html_message)
        
        # Scroll to the bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )