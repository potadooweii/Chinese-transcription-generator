import os

from backend.file.file_manager import FileManager
from backend.transcription import WhisperModelArgs
from backend.transcription.diarizer import Diarizer
from backend.transcription.transcriptor import Transcriptor


class TranscriptionManager:
    def __init__(self):
        self._file_manager = FileManager()

    def run(self, audio_name: str, whisper_model_args: dict, diarization: bool):
        work_dir = self._file_manager.setup_temp(audio_name)

        audio_path = os.path.join(work_dir, audio_name)
        whisper_model_args = WhisperModelArgs.parse_obj(whisper_model_args)

        transcriptor = Transcriptor(whisper_model_args)
        diarizer = Diarizer(work_dir)

        res = transcriptor.transcribe(audio_path)
        if diarization:
            speaker_timestamp = diarizer.diarize(audio_path)
            res = self._get_speaker_mapping(res["segments"], speaker_timestamp)

        self._file_manager.cleanup_temp()

        self._file_manager.write_result_to_download(res)

    def _get_speaker_mapping(self, wrd_ts, spk_ts):
        s, e, sp = spk_ts[0]
        wrd_pos, turn_idx = 0, 0
        wrd_spk_mapping = []
        for wrd_dict in wrd_ts:
            ws, we, wrd = (
                int(wrd_dict["start"] * 1000),
                int(wrd_dict["end"] * 1000),
                wrd_dict["text"],
            )
            wrd_pos = ws
            while wrd_pos > float(e):
                turn_idx += 1
                turn_idx = min(turn_idx, len(spk_ts) - 1)
                s, e, sp = spk_ts[turn_idx]
                if turn_idx == len(spk_ts) - 1:
                    e = we
            wrd_spk_mapping.append(
                {"text": wrd, "start_time": ws, "end_time": we, "speaker": sp}
            )
        return wrd_spk_mapping


if __name__ == "__main__":
    tm = TranscriptionManager()
    tm.run("short.m4a", {}, True)
