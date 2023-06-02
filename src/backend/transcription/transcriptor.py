import gc

import torch.cuda as cuda
import whisperx
from pydantic import BaseModel

from backend.transcription import WhisperModelArgs


class Transcriptor:
    def __init__(self, model_args: WhisperModelArgs):
        self.model_args = model_args

    def transcribe(self, audio_path):
        model_args = self.model_args
        model_args.device = (
            model_args.device if model_args.device else self._get_available_device()
        )

        # transcribe
        whisper_model = self._load_whisper_model(model_args)
        audio = whisperx.load_audio(audio_path)
        transcribe_result = whisper_model.transcribe(
            audio,
            batch_size=self.model_args.batch_size,
        )
        gc.collect()
        cuda.empty_cache()
        del whisper_model

        # align
        align_model, metadata = whisperx.load_align_model(
            language_code=transcribe_result["language"], device=model_args.device
        )
        align_result = whisperx.align(
            transcribe_result["segments"],
            align_model,
            metadata,
            audio,
            model_args.device,
            return_char_alignments=False,
        )
        gc.collect()
        cuda.empty_cache()
        del align_model

        return align_result

    def _load_whisper_model(self, model_args: WhisperModelArgs):
        asr_options = {
            "initial_prompt": "以下是一段繁體中文的逐字稿：這是第一句，這是第二句。",
        }
        return whisperx.load_model(
            "tiny",
            model_args.device,
            compute_type=model_args.compute_type,
            asr_options=asr_options,
        )

    def _get_available_device(self):
        if cuda.is_available():
            return "cuda"
        else:
            return "cpu"
