import subprocess
import uuid


class Scdl:
    """
    Class which calls the scdl command line tool to download songs from soundcloud
    """

    def __init__(self, path="plugins/play/audio", max_size="15mb"):
        """
        Initialize the scdl library
        :param max_size: the maximum size of a song in mb (default 15mb)
        """
        self.path = path
        self.max_size = max_size

    def download(self, url, file_name=None):
        """
        Helper to download a song from soundcloud
        :param url: the full url to the song
        :param file_name: optional file name to save the file as
        :return: A dict with the file path, message, and the result of the download
        """
        # If the file_name was provided, use it, otherwise generate a random one
        if file_name:
            output_file = file_name
        else:
            output_file = f"{uuid.uuid4()}"

        process = subprocess.Popen(
            [
                "scdl",
                "--hide-progress",
                "--error",
                "--overwrite",
                "--onlymp3",
                "--max-size",
                self.max_size,
                "--path",
                self.path,
                "--name-format",
                output_file,
                "-l",
                url,
            ],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, _ = process.communicate()

        message = stdout.strip()

        # If the message is not blank, it means there was an error
        if message != "":
            # If the URL was not valid, return a message
            if "URL is not valid" in message:
                return {
                    "file_path": None,
                    "message": "URL is not valid",
                    "result": False,
                }
            if "File not within --min-size and --max-size bounds" in message:
                return {
                    "file_path": None,
                    "message": f"File exceeds max size of {self.max_size}",
                    "result": False,
                }
            # In any other case, return the error message
            return {
                "path": None,
                "result": False,
                "message": message,
            }
        # If the message is blank, it means the download was successful
        else:
            return {
                "path": f"{self.path}/{output_file}.mp3",
                "result": True,
                "message": None,
            }
