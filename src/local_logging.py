import logging

def get_logger():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/log_file.log", mode= 'w'),
            logging.StreamHandler(), 
        ]
    )
    logger = logging.getLogger()
    return logger