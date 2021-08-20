from datetime import datetime

class Util:
    """
    A collection of common utilities used throughout the repo
    """
    def iso_timestamp(self):
        return datetime.now().replace(microsecond=0).isoformat()