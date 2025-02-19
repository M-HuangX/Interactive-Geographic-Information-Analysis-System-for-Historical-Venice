# src/core/chat_manager.py
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage
from typing import Optional

class ChatManager:
    def __init__(self, api_key: str, model: str):
        self.client = ChatAnthropic(
            anthropic_api_key=api_key,
            max_tokens_to_sample=8192,
            model=model
        )
        self.history = []
    
    def add_message(self, message: str, is_user: bool):
        """Add message to history"""
        try:
            msg = HumanMessage(content=message) if is_user else AIMessage(content=message)
            self.history.append(msg)
        except Exception as e:
            print(f"Error adding message to history: {e}")
    
    def get_response(self, system_prompt: str) -> Optional[str]:
        """Get AI response"""
        try:
            messages = [HumanMessage(content=system_prompt)] + self.history
            response = self.client.invoke(messages)
            
            # Check response type and content
            if not response or not hasattr(response, 'content'):
                print("Invalid response from API")
                return None
                
            return response.content
            
        except Exception as e:
            print(f"Error getting response from API: {e}")
            return None