# src/main.py
import logging
import sys
from PyQt6.QtWidgets import QApplication
from .core.config_loader import ConfigLoader
from .ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app_debug.log', encoding='utf-8')
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.debug("Application starting...")
    
    app = QApplication(sys.argv)
    
    try:
        config = ConfigLoader.load_config()
        prompts = ConfigLoader.load_prompts()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    window = MainWindow(config, prompts)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()