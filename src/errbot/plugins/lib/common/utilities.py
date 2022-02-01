import hashlib
import time
import urllib.parse
from datetime import datetime, timedelta
from difflib import get_close_matches

import psutil


class Util:
    """
    A collection of common utilities used throughout the repo
    """
  
    def close_matches(self, word, patterns):
        """
        Given a word and a list of possible patterns, return a list of close matches
        :param word: The word to search for (String)
        :param patterns: A list of possible patterns (List of Strings)
        :return: A list of close matches (List of Strings)
        """
        return get_close_matches(word, patterns)

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

    def is_timestamp_older_than_n_seconds(self, timestamp, seconds):
        """
        Given a timestamp and N seconds, check the timestamp
        :return: True if timestamp is older than N seconds, False otherwise
        """
        expiration = datetime.utcnow() - timedelta(seconds=seconds)

        if timestamp < expiration:
            return True

        else:
            return False

    def when_ready_timestamp(self, timestamp, seconds):
        """
        Given X seconds in the future, determine when a timestamp is considered ready
        :return: a dict with hours_minutes_seconds() like formatting
        """
        ready = timestamp + timedelta(seconds=seconds)
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

    def is_file_open(self, file_path):
        """
        Checks if a file is open
        :return: True if file is open, False if not
        Note: will return False if file does not exist which is okay
        Example: is_file_open('test.txt')
        """
        for proc in psutil.process_iter():
            try:
                flist = proc.open_files()
                if flist:
                    for nt in flist:
                        if file_path in nt.path:
                            # File is open so we return True
                            return True
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                pass
        # File is either closed or not found so we return False
        return False

    def check_file_ready(self, file_path, retries=5, sleep_time=0.1):
        """
        Helper function to check if a file is ready to be opened
        Use in conjunction with is_file_open()
        :return: True if file is ready, False if not
        """
        for _ in range(retries):
            if self.is_file_open(file_path):
                # File is still open so we will sleep
                time.sleep(sleep_time)
            else:
                # The file is not open and ready
                return True

        # The file was not deemed ready after retries
        return False
