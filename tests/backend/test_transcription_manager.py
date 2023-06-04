import unittest
from unittest.mock import patch
import os
from backend import SERVICE_ENV
from backend.transcription.transcription_manager import TranscriptionManager

class TestTranscriptionManager(unittest.TestCase):

    def test_run(self):
        # setup
        transcription_manager = TranscriptionManager()
        audio_path = "tests/testsets/audio/test.m4a"
        audio_name = "test.m4a"
        with open(audio_path, 'rb') as f:
            audio = f.read()
            transcription_manager._file_manager.save_audio(audio_name, audio)


        with self.subTest("Happy Path 1"):
            ret = transcription_manager.run(audio_name)
            self.assertTrue(ret)

        with self.subTest("Happy Path 2"):
            ret = transcription_manager.run(audio_name, diarization=False)
            self.assertTrue(ret)

        # cleanup
        transcription_manager._file_manager.delete_file(
            os.path.join(SERVICE_ENV.UPLOAD_DIR, audio_name)
        )
        transcription_manager._file_manager.delete_file(
            os.path.join(SERVICE_ENV.DOWNLOAD_DIR, audio_name+'.txt')
        )