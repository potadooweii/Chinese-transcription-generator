import unittest
from unittest.mock import patch
import torch.cuda as cuda
from backend.transcription import WhisperModelArgs
from backend.transcription.transcriptor import Transcriptor


class TestTranscriptor(unittest.TestCase):
    def test_transcribe(self):
        transcriptor = Transcriptor()
        audio_path = "tests/testsets/audio/test.m4a"
        no_audio_path = "tests/testsets/audio/no_audio.m4a"

        with self.subTest("Naive Transcribe using GPU if any"):
            ret = transcriptor.transcribe(audio_path)
            self.assertNotEqual(len(ret), 0)

        with self.subTest("Naive Transcribe using CPU."):
            with patch.object(cuda, "is_available", return_value=False):
                ret = transcriptor.transcribe(audio_path)
                self.assertNotEqual(len(ret), 0)

        with self.subTest("Not exists"):
            ret = transcriptor.transcribe(no_audio_path)
            self.assertEqual(len(ret), 0)

        with self.subTest("Customized settings"):
            args = WhisperModelArgs(device="cuda")
            ret = transcriptor.transcribe(audio_path, args)
            self.assertNotEqual(len(ret), 0)
