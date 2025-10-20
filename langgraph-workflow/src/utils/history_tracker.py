import os

HISTORY_ID_FILE = "last_history_id.txt"


def get_last_history_id():
    """Read the last processed history ID from a file."""
    if os.path.exists(HISTORY_ID_FILE):
        with open(HISTORY_ID_FILE, "r") as f:
            return int(f.read().strip())
    return None


def save_last_history_id(history_id):
    """Save the last processed history ID to a file."""
    with open(HISTORY_ID_FILE, "w") as f:
        f.write(str(history_id))
