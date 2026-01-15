import logging
from pathlib import Path as path

log_dir = path("logs")
log_dir.mkdir(exist_ok=True)

def get_logger(name:str="log_file"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(log_dir / "log_file.log", mode='a')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  
        )
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    return logger
