import unittest
from unittest.mock import Mock, patch
import os
from backend import SERVICE_ENV
from backend.file.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    def test_write_result_to_download(self):
        with self.subTest("Naive Transcription Case"):
            result = [{"text": "hello,"}, {"text": "world!"}]
            file_name = "a_test_case"
            FileManager.write_result_to_download(result, file_name, False)
            output_file = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, file_name + ".txt")

            self.assertTrue(os.path.exists(output_file))
            with open(output_file) as f:
                for idx, line in enumerate(f.readlines()):
                    self.assertEqual(result[idx]["text"] + "\n", line)

            # clenup
            os.remove(output_file)

        with self.subTest("With Diarization Case"):
            result = [
                {"speaker": 0, "text": "hello, world!"},
                {"speaker": 1, "text": "hello!"},
            ]
            file_name = "a_test_case"
            FileManager.write_result_to_download(result, file_name, True)
            output_file = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, file_name + ".txt")

            self.assertTrue(os.path.exists(output_file))
            with open(output_file) as f:
                for idx, line in enumerate(f.readlines()):
                    ans = f'Speaker {result[idx]["speaker"]}: {result[idx]["text"]}\n'
                    self.assertEqual(ans, line)

            # clenup
            os.remove(output_file)

    @patch.object(os, "listdir")
    def test_get_files(self, mock_listdir: Mock):
        with self.subTest("Naive Upload Case"):
            fake_upload_files = ["1.m4a", "2.mp3"]
            mock_listdir.return_value = fake_upload_files
            files = FileManager.get_upload_files()
            self.assertEqual(fake_upload_files, files)

        with self.subTest("Search Upload Case"):
            fake_upload_files = ["1.m4a", "2.mp3"]
            mock_listdir.return_value = fake_upload_files
            files = FileManager.get_upload_files(pattern="m4a")
            self.assertEqual([fake_upload_files[0]], files)

        with self.subTest("Naive Download Case"):
            fake_download_files = ["1.txt", "2.txt"]
            mock_listdir.return_value = fake_download_files
            files = FileManager.get_download_files()
            self.assertEqual(fake_download_files, files)

    def test_save_audio(self):
        with self.subTest("Audio Case"):
            audio = b"0x123"
            audio_name = "a_test_case.mp3"
            FileManager.save_audio(audio_name, audio)

            output_file = os.path.join(SERVICE_ENV.UPLOAD_DIR, audio_name)
            with open(output_file, "rb") as f:
                self.assertEqual(audio, f.read())

        # cleanup
        os.remove(output_file)

    def test_delete_file(self):
        with self.subTest("Download Case"):
            test_file = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, "a_test_case.txt")
            with open(test_file, "w") as f:
                f.write("test")
            try:
                FileManager.delete_file(test_file)
                self.assertFalse(os.path.exists(test_file))
            except:
                os.remove(test_file)

        with self.subTest("Upload Case"):
            test_file = os.path.join(SERVICE_ENV.UPLOAD_DIR, "a_test_case.txt")
            with open(test_file, "w") as f:
                f.write("test")
            try:
                FileManager.delete_file(test_file)
                self.assertFalse(os.path.exists(test_file))
            except:
                os.remove(test_file)
