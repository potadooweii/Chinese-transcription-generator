import os
import tempfile

from backend import SERVICE_ENV


class FileManager:
    def setup_temp(self, audio_name: str) -> str:
        self.work_dir = tempfile.TemporaryDirectory()
        os.system(
            f"copy {os.path.join(SERVICE_ENV.UPLOAD_DIR, audio_name)} {self.work_dir.name}"
        )
        return self.work_dir.name

    def cleanup_temp(self):
        if self.work_dir:
            self.work_dir.cleanup()

    @staticmethod
    def write_result_to_download(result: list[dict], file_name: str, diarization: bool = True):
        file_path = os.path.join(SERVICE_ENV.DOWNLOAD_DIR, file_name+'.txt')
        with open(file_path, 'w') as f:
            for segment in result:
                prefix = f"Speaker {segment['speaker']}: " if diarization else ""
                a_line = prefix + f"{segment['text'].strip()}"
                print(a_line, file=f)

    @staticmethod
    def get_upload_files(pattern: str = "", abs_path: bool = False):
        files = os.listdir(SERVICE_ENV.UPLOAD_DIR)
        ret = [f for f in files if f.endswith(".mp3") or f.endswith(".m4a")]
        if pattern:
            ret = [f for f in ret if pattern.lower() in f.lower()]

        if abs_path:
            ret = [os.path.join(SERVICE_ENV.UPLOAD_DIR, f) for f in ret]

        return ret

    @staticmethod
    def get_download_files(pattern: str = "", abs_path: bool = False):
        files = os.listdir(SERVICE_ENV.DOWNLOAD_DIR)
        ret = [f for f in files if f.endswith(".txt") or f.endswith(".srt")]
        if pattern:
            ret = [f for f in ret if pattern.lower() in f.lower()]

        if abs_path:
            ret = [os.path.join(SERVICE_ENV.DOWNLOAD_DIR, f) for f in ret]

        return ret

    @staticmethod
    def save_audio(filename: str, audio: bytes):
        file_path = os.path.join(SERVICE_ENV.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(audio)

    @staticmethod
    def delete_file(file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
