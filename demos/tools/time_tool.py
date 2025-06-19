from datetime import datetime, timezone
import json


def current_time():
    """Returns the current time in HH:MM:SS format."""

    return json.dumps({"current_time": datetime.now().isoformat()})
