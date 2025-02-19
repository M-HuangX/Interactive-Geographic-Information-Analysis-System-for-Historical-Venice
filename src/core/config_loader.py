# src/core/config_loader.py
import json
import os

class ConfigLoader:
    @staticmethod
    def load_config():
        with open('config/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def load_prompts():
        with open('config/prompts.json', 'r', encoding='utf-8') as f:
            return json.load(f)