<h1 align="center">Chinese Transcription Server</h1>

<p align="center">
    <a href="">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab">
    </a>
    <a href="">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit">
    </a>
</p>

Using Whisper & NeMo to transcribe and diarize audio. (Chinese friendly.)

# Setup

## Prerequisites

* `ffmpeg`
```
# on Ubuntu or Debian
$ sudo apt update && sudo apt install ffmpeg

# on Arch Linux
$ sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
$ brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
$ choco install ffmpeg
```

* `conda`
```
$ wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ chmod 777 Miniconda3-latest-Linux-x86_64.sh
$ sh Miniconda3-latest-Linux-x86_64.sh
$ conda create --name whisper_service python=3.10
```

## Installation
After clone this project: 
```
$ conda activate whisper_service
$ conda develop src/
$ conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia
$ pip install -r requirements.txt
```


## Executing program
```
$ streamlit run src/frontend/app.py
```


## Acknowledgments
Inspiration, code snippets, etc.
* [whisper-diarization](https://github.com/matiassingers/awesome-readme)
* [whisperX](https://github.com/m-bain/whisperX)
* [Nvidia NeMo](https://github.com/NVIDIA/NeMo)