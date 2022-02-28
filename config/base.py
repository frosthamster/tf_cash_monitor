from pathlib import Path


PROJECT_DIR = Path(__file__).parent.parent

POLL_DELAY_SECONDS = 60

ALERT_PATH = PROJECT_DIR / 'alert.flac'

API_URL = 'https://api.tinkoff.ru/geo/withdraw/clusters'

# Yekaterinburg + Ber
QUERY_BOTTOM_LEFT_LAT = 56.67933199407095
QUERY_BOTTOM_LEFT_LNG = 60.31839438665731
QUERY_TOP_RIGHT_LAT = 56.98835431334478
QUERY_TOP_RIGHT_LNG = 60.86565085638387
QUERY_ZOOM = 11

SKIP_ATMS_IDS = set()
CURRENCY_FILTERS_AMOUNT_GT = {
    'EUR': 4000,
}

# LOG Config
LOG_ELK_URL = ''
LOG_FORMATTER = 'default'
LOG_LEVEL = 'INFO'
LOG_SETTINGS = lambda conf: {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': conf['LOG_FORMATTER'],
        },
    },
    'loggers': {
        '': {
            'level': conf['LOG_LEVEL'],
            'handlers': ['stdout'],
        },
    }
}
