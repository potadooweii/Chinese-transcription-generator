import unittest
from unittest.mock import Mock, patch
import os
from backend import SERVICE_ENV
from backend.transcription.diarizer import Diarizer
import shutil


class TestDiarizer(unittest.TestCase):
    def test_init(self):
        with self.subTest("Absent work_dir"):
            work_dir = "tests/a_test_case/"
            diarizer = Diarizer(work_dir)
            self.assertTrue(os.path.exists(work_dir))
            created_dir = os.path.join(work_dir, "diarization")
            self.assertTrue(os.path.exists(created_dir))

        # cleanup
        shutil.rmtree(work_dir)

    def test_diarization(self):
        work_dir = "tests/a_test_case/"
        diarizer = Diarizer(work_dir)

        with self.subTest("Diarize"):
            audio_path = "tests/testsets/audio/no_audio.m4a"
            ret = diarizer.diarize(audio_path)
            self.assertListEqual(ret, [])

        with self.subTest("Diarize"):
            audio_path = "tests/testsets/audio/test.m4a"
            ret = diarizer.diarize(audio_path)
            self.assertTrue(isinstance(ret, list))
            self.assertNotEqual(len(ret), 0)

        # cleanup
        shutil.rmtree(work_dir)
