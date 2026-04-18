from datetime import datetime

LOG_FILE = 'log.txt'

def log_update(message):
    with open(LOG_FILE, 'a+') as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")