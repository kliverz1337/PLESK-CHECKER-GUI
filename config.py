import os

# API Configuration
BASE_URL = "" # Not directly used in this script, but good to have for future expansion
RETRY_COUNT = 2
BACKOFF_FACTOR = 0.5
STATUS_FORCELIST = [500, 502, 503, 504]
TIMEOUT = 20

# File Paths
OUTPUT_FILE_STATUS = 'valid_plesk_status.txt'
OUTPUT_FILE_LOGINS = 'valid_plesk_logins.txt'

# GUI Configuration
APP_TITLE = "PLESK CHECKER GUI"
APP_GEOMETRY = "900x650"
APP_MINSIZE = (700, 500)
APPEARANCE_MODE = "Light"
COLOR_THEME = "blue"
