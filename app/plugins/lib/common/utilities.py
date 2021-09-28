import hashlib
from datetime import datetime
import urllib.parse


class Util:
    """
    A collection of common utilities used throughout the repo
    """

    def iso_timestamp(self):
        """
        Return a ISO formatted timestamp of the current time
        """
        return datetime.now().replace(microsecond=0).isoformat()

    def sha256(self, data):
        """
        Hash a string and return a SHA256 hash
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def hours_minutes_seconds(self, seconds):
        """
        Get the hours, munutes and seconds from a given number of seconds
        """
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60

        return {"hours": h, "minutes": m, "seconds": s}

    def hours_minutes_seconds_from_ms(self, ms):
        """
        Get the hours, munutes and seconds from a given number of milliseconds
        """
        return self.hours_minutes_seconds(int(ms / 1000))

    def url_encode(self, string):
        """
        url encode a string
        """
        return urllib.parse.quote(string)
