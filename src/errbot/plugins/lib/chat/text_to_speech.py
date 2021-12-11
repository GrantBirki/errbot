# Convert text to speech as a mp3 file
# TTS helper class

from gtts import gTTS
import uuid


class TextToSpeech:
    def __init__(
        self, language="en", tld="com.au", slow=False, path="plugins/tts/audio"
    ):
        self.language = language
        self.tld = tld
        self.slow = slow
        self.path = path

    def convert_to_mp3(self, text):
        speech_obj = gTTS(text=text, lang=self.language, slow=self.slow, tld=self.tld)
        output_file = f"{self.path}/{uuid.uuid4()}.mp3"
        speech_obj.save(output_file)
        return output_file
