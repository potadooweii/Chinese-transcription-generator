import gc
import os

import GPUtil
import torch.cuda as cuda
import whisperx

from backend.transcription import WhisperModelArgs


class Transcriptor:

    def transcribe(self, audio_path: str, model_args: WhisperModelArgs = WhisperModelArgs()) -> str:
        if not os.path.exists(audio_path):
            return []

        model_args.device = (
            model_args.device if model_args.device else self._get_available_device()
        )

        # transcribe
        try:
            whisper_model = self._load_whisper_model(model_args)
        except Exception as e:
            print(e)
            return []
        
        audio = whisperx.load_audio(audio_path)
        transcribe_result = whisper_model.transcribe(
            audio,
            batch_size=model_args.batch_size,
        )
        gc.collect(); cuda.empty_cache(); del whisper_model

        # align
        align_model, metadata = whisperx.load_align_model(
            language_code=transcribe_result["language"], device=model_args.device
        )
        ret = whisperx.align(
            transcribe_result["segments"],
            align_model,
            metadata,
            audio,
            model_args.device,
            return_char_alignments=False,
        )
        gc.collect(); cuda.empty_cache(); del align_model

        return ret

    def _load_whisper_model(self, model_args: WhisperModelArgs):
        if str.isdigit(model_args.device[-1]):
            device, device_index = model_args.device.split(':')
        else:
            device = model_args.device
            device_index = 0
        return whisperx.load_model(
            "tiny",
            device,
            device_index=int(device_index),
            compute_type=model_args.compute_type,
            asr_options={
                "initial_prompt": "以下是一段繁體中文的逐字稿：這是第一句，這是第二句。",
            },
        )

    def _get_available_device(self):
        if cuda.is_available():
            deviceID = GPUtil.getAvailable(maxLoad=0.5, maxMemory=0.5)
            if len(deviceID) > 0:
                return f"cuda:{deviceID[0]}"
        return "cpu"
