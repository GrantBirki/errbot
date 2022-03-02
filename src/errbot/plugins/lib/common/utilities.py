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

    def hrs_to_milliseconds(self, num):
        """
        Convert hours to milliseconds
        :param num: number of hours
        :return: milliseconds (Int)
        """
        return 1000 * 60 * 60 * num

    def utc_milli_timestamp(self):
        """
        Get current UTC time in milliseconds
        :return: UTC time in milliseconds (Int)
        """
        return int(datetime.utcnow().timestamp()) * 1000

    def close_matches(self, word, patterns, cutoff=0.6):
        """
        Given a word and a list of possible patterns, return a list of close matches
        :param word: The word to search for (String)
        :param patterns: A list of possible patterns (List of Strings)
        :param cutoff: The cutoff to determine if a pattern is a match (Float)
        :return: A list of close matches (List of Strings)
        """
        return get_close_matches(word, patterns, cutoff=cutoff)

    def iso_timestamp(self):
        """
        Helper function to return a ISO formatted timestamp
        :return: an ISO formatted timestamp of the current time
        """
        return datetime.utcnow().replace(microsecond=0).isoformat()

    def parse_iso_timestamp(self, timestamp):
        """
        Parse a ISO formatted timestamp and return a datetime object
        Used in conjunction with iso_timestamp()
        :param timestamp: The ISO formatted timestamp (String)
        :return: A datetime object
        """
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    def is_timestamp_older_than_n_seconds(self, timestamp, seconds):
        """
        Given a timestamp and N seconds, check the timestamp
        :param timestamp: The timestamp to check (DateTime object)
        :param seconds: The number of seconds to check (Integer)
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
        :param timestamp: The timestamp to check (DateTime object)
        :param seconds: The number of seconds to check (Integer)
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
        :param hms: A dict of hours, minutes and seconds (Dict)
        :return: A string of the form "H:## M:## S:##"
        """
        hours = int(hms.get("hours", 0))
        minutes = int(hms.get("minutes", 0))
        seconds = int(hms.get("seconds", 0))
        return f"H:{hours} M:{minutes} S:{seconds}"

    def sha256(self, data):
        """
        Hash a string and return a SHA256 hash
        :param data: The string to hash (String)
        :return: A SHA256 hash of the string (String)
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def hours_minutes_seconds(self, seconds):
        """
        Get the hours, munutes and seconds from a given number of seconds
        :param seconds: The number of seconds to convert (Integer)
        :return: A dict of hours, minutes and seconds (Dict)
        """
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60

        return {"hours": h, "minutes": m, "seconds": s}

    def hours_minutes_seconds_from_ms(self, ms):
        """
        Get the hours, munutes and seconds from a given number of milliseconds
        :param ms: The number of milliseconds to convert (Integer)
        :return: A dict of hours, minutes and seconds (Dict)
        """
        return self.hours_minutes_seconds(int(ms / 1000))

    def url_encode(self, string):
        """
        url encode a string
        :param string: The string to encode (String)
        :return: The url encoded string (String)
        """
        return urllib.parse.quote(string)

    def is_file_open(self, file_path):
        """
        Checks if a file is open
        :param file_path: The path to the file to check (String)
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
        :param file_path: The path to the file to check (String)
        :param retries: The number of times to check if the file is ready (Integer)
        :param sleep_time: The number of seconds to sleep between checks (Float)
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
