import hashlib
from datetime import datetime, timedelta
import urllib.parse


class Util:
    """
    A collection of common utilities used throughout the repo
    """

    def iso_timestamp(self):
        """
        Return a ISO formatted timestamp of the current time
        """
        return datetime.utcnow().replace(microsecond=0).isoformat()

    def parse_iso_timestamp(self, timestamp):
        """
        Parse a ISO formatted timestamp and return a datetime object
        Used in conjunction with iso_timestamp()
        """
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    def is_timestamp_older_than_n_days(self, timestamp, days):
        """
        Given a timestamp and N days, check the timestamp
        :return: True if timestamp is older than N days, False otherwise
        """
        expiration = datetime.utcnow() - timedelta(days=days)

        if timestamp < expiration:
            return True

        else:
            return False

    def when_ready_timestamp(self, timestamp, days):
        """
        Given X days in the future, determine when a timestamp is considered ready
        :return: a dict with hours_minutes_seconds() like formatting
        """
        ready = timestamp + timedelta(days=days)
        now = datetime.utcnow()
        delta = ready - now
        total_seconds = delta.total_seconds()
        return self.hours_minutes_seconds(total_seconds)

    def fmt_hms(self, hms):
        """
        Format a dict of hours, minutes and seconds into a string
        """
        hours = int(hms.get("hours", 0))
        minutes = int(hms.get("minutes", 0))
        seconds = int(hms.get("seconds", 0))
        return f"H:{hours} M:{minutes} S:{seconds}"

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
