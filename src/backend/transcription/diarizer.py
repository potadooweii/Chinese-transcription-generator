import gc
import json
import os

import librosa
import soundfile
import torch.cuda as cuda
import wget
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from omegaconf import OmegaConf


class Diarizer:
    def __init__(self, work_dir: str):
        self.work_dir = os.path.join(work_dir, "diarization")
        os.makedirs(self.work_dir)

    def diarize(self, audio_path: str):
        audio_path = self._audio_to_mono(audio_path)
        msdd_model = NeuralDiarizer(cfg=self._create_config(audio_path))
        msdd_model.diarize()

        gc.collect()
        cuda.empty_cache()
        del msdd_model
        return self._get_speaker_timestamp()

    def _audio_to_mono(self, audio_path: str):
        signal, sample_rate = librosa.load(audio_path, sr=None)
        output_path = os.path.join(self.work_dir, "mono_file.wav")
        soundfile.write(output_path, signal, sample_rate, "PCM_24")
        return output_path

    def _get_speaker_timestamp(self):
        output_file_path = os.path.join(
            self.work_dir,
            "nemo_outputs",
            "pred_rttms",
            "mono_file.rttm",
        )

        speaker_ts = []
        with open(output_file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line_list = line.split(" ")
                s = int(float(line_list[5]) * 1000)
                e = s + int(float(line_list[8]) * 1000)
                speaker_ts.append([s, e, int(line_list[11].split("_")[-1])])

        return speaker_ts

    def _create_config(self, audio_path: str):
        DOMAIN_TYPE = "telephonic"  # Can be meeting or telephonic based on domain type of the audio file
        CONFIG_FILE_NAME = f"diar_infer_{DOMAIN_TYPE}.yaml"
        CONFIG_URL = f"https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/{CONFIG_FILE_NAME}"
        MODEL_CONFIG = os.path.join(self.work_dir, CONFIG_FILE_NAME)
        if not os.path.exists(MODEL_CONFIG):
            MODEL_CONFIG = wget.download(CONFIG_URL, self.work_dir)

        config = OmegaConf.load(MODEL_CONFIG)

        data_dir = os.path.join(self.work_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        meta = {
            "audio_filepath": audio_path,
            "offset": 0,
            "duration": None,
            "label": "infer",
            "text": "-",
            "rttm_filepath": None,
            "uem_filepath": None,
        }
        manifest_filepath = os.path.join(data_dir, "input_manifest.json")
        with open(manifest_filepath, "w") as fp:
            json.dump(meta, fp)
            fp.write("\n")

        pretrained_vad = "vad_multilingual_marblenet"
        pretrained_speaker_model = "titanet_large"

        config.num_workers = (
            0  # Workaround for multiprocessing hanging with ipython issue
        )

        output_dir = os.path.join(self.work_dir, "nemo_outputs")
        os.makedirs(output_dir, exist_ok=True)
        config.diarizer.manifest_filepath = manifest_filepath
        config.diarizer.out_dir = (
            output_dir  # Directory to store intermediate files and prediction outputs
        )

        config.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
        config.diarizer.oracle_vad = (
            False  # compute VAD provided with model_path to vad config
        )
        config.diarizer.clustering.parameters.oracle_num_speakers = False

        # Here, we use our in-house pretrained NeMo VAD model
        config.diarizer.vad.model_path = pretrained_vad
        config.diarizer.vad.parameters.onset = 0.8
        config.diarizer.vad.parameters.offset = 0.6
        config.diarizer.vad.parameters.pad_offset = -0.05
        config.diarizer.msdd_model.model_path = (
            "diar_msdd_telephonic"  # Telephonic speaker diarization model
        )

        return config
