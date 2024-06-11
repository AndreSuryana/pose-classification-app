import os
import time

# Define log levels and their numeric values
LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'ERROR': 30,
    'ALL': 0,  # 'ALL' means all log levels will be logged
}

# Predefine colors
COLORS = {
    'DEBUG': '',
    'INFO': '\033[34m',  # Blue
    'ERROR': '\033[31m',  # Red
    'RESET': '\033[0m'  # Reset to default color
}

# Set log level from environment variable, default to 'ALL'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'ALL').upper()
current_log_level = LOG_LEVELS.get(LOG_LEVEL, LOG_LEVELS['ALL'])

def should_log(level):
    """Check if the current log level allows logging of the given level."""
    return level >= current_log_level

def log_message(level, label, message, *args):
    if should_log(level):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        color_code = COLORS[label]
        reset_code = COLORS['RESET']
        if args:
            args_str = ' '.join(map(str, args))
            print(f'{color_code}{timestamp} [{label[0]}]: {message} {args_str}{reset_code}')
        else:
            print(f'{color_code}{timestamp} [{label[0]}]: {message}{reset_code}')

def d(message, *args):
    log_message(LOG_LEVELS['DEBUG'], 'DEBUG', message, *args)

def i(message, *args):
    log_message(LOG_LEVELS['INFO'], 'INFO', message, *args)

def e(message, *args):
    log_message(LOG_LEVELS['ERROR'], 'ERROR', message, *args)