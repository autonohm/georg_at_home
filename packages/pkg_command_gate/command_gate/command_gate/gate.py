"""Gate logic without ROS, so it can be tested with plain pytest."""

import os

ALLOWED_MODE = 'real'
DEFAULT_MODE_FILE = '/etc/georg/mode'


def read_mode_file(path: str = DEFAULT_MODE_FILE) -> str:
    """Return the device mode from the mode file, or '' if it is missing or unreadable."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''


def device_mode() -> str:
    """Device mode: the mode file if present, else GEORG_DEVICE_MODE (set by projectctl.bash)."""
    mode = read_mode_file(os.environ.get('GEORG_MODE_FILE', DEFAULT_MODE_FILE))
    if mode:
        return mode
    return os.environ.get('GEORG_DEVICE_MODE', '').strip()


def is_open(device: str, profile: str) -> bool:
    """Forward only if both the device and the started profile are 'real'. Fail closed."""
    return device == ALLOWED_MODE and profile.strip() == ALLOWED_MODE
