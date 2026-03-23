"""
Centralized logger for E-Mapp backend.
Outputs colored, structured logs to terminal.
"""
import logging
import sys
from datetime import datetime

# ANSI color codes (works on Windows 11 + modern terminals)
RESET  = '\033[0m'
BOLD   = '\033[1m'
GRAY   = '\033[90m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
CYAN   = '\033[96m'
MAGENTA= '\033[95m'
WHITE  = '\033[97m'

LEVEL_COLORS = {
    'DEBUG':    GRAY,
    'INFO':     GREEN,
    'WARNING':  YELLOW,
    'ERROR':    RED,
    'CRITICAL': f'{BOLD}{RED}',
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelname, RESET)
        time_str = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        level    = f'{color}{record.levelname:<8}{RESET}'
        name     = f'{CYAN}{record.name}{RESET}'
        msg      = record.getMessage()

        # Color message based on level
        if record.levelno >= logging.ERROR:
            msg = f'{RED}{msg}{RESET}'
        elif record.levelno >= logging.WARNING:
            msg = f'{YELLOW}{msg}{RESET}'

        line = f'{GRAY}[{time_str}]{RESET} {level} {name}: {msg}'

        # Append exception traceback
        if record.exc_info:
            line += '\n' + self.formatException(record.exc_info)

        return line


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that writes colored output to stdout (UTF-8 safe)."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Force UTF-8 on Windows to handle Vietnamese and Unicode characters
        if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
            import io
            stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        else:
            stream = sys.stdout
        handler = logging.StreamHandler(stream)
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    logger.setLevel(logging.DEBUG)
    return logger


# ── Request/response helper (used by server.py) ───────────────────────────────
def log_request(logger: logging.Logger, method: str, path: str) -> None:
    logger.info(f'→ {BOLD}{method}{RESET} {WHITE}{path}{RESET}')


def log_response(logger: logging.Logger, method: str, path: str,
                 status: int, elapsed_ms: float) -> None:
    if status >= 500:
        color = RED
    elif status >= 400:
        color = YELLOW
    else:
        color = GREEN
    logger.info(
        f'← {color}{status}{RESET} {BOLD}{method}{RESET} '
        f'{WHITE}{path}{RESET} {GRAY}({elapsed_ms:.0f}ms){RESET}'
    )
