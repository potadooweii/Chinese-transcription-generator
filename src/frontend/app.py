import threading
import time

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_autorefresh import st_autorefresh
from streamlit_server_state import server_state, server_state_lock

from backend.file.file_manager import FileManager
from backend.transcription.transcription_manager import TranscriptionManager


def run_transcription(
    audio: str, whisper_model_args: dict = {}, diarization: bool = True
):
    try:
        transcription_manager = TranscriptionManager()
        transcription_manager.run(audio, whisper_model_args, diarization)
    except Exception as e:
        print(e)
        st.warning(e)
    
    # check if there is queued job.
    if len(server_state.job_queue) > 0:
        next_audio = server_state.job_queue.pop()
        start_a_transcribing_task(next_audio)
    else:
        with server_state_lock.running_file:
            server_state.running_file = ""


def start_a_transcribing_task(audio: str):
    with server_state_lock.running_file:
        server_state.running_file = audio
    thread = threading.Thread(target=run_transcription, args=(audio,))
    add_script_run_ctx(thread)
    thread.start()


def nothing_running_view():
    menu_options = FileManager.get_upload_files()
    selected_audio = st.selectbox("Select a audio.", menu_options)
    run_button_clicked = st.button("Run!")

    if run_button_clicked:
        st.write("You selected:", selected_audio)
        time.sleep(1)
        start_a_transcribing_task(selected_audio)
        st.experimental_rerun()


def something_running_view():
    st.write(f"{server_state.running_file} is being transcribed...")
    # progress_bar = st.progress(server_state.progress) # TODO

    st.subheader("Job queue:")
    for i, job in enumerate(server_state.job_queue):
        col0, col1, col2 = st.columns(3)
        with col0:
            st.write(i)
        with col1:
            st.write(job)
        with col2:
            if st.button("delete", key="delete" + job):
                with server_state_lock.job_queue:
                    server_state.job_queue.remove(job)
                st.experimental_rerun()

    st.subheader("Add Job to queue:")
    menu_options = FileManager.get_upload_files()
    selected_audio = st.selectbox("Select a audio.", menu_options)
    submit_button_clicked = st.button("Submit")

    if submit_button_clicked:
        with server_state_lock.job_queue:
            if selected_audio not in server_state.job_queue:
                server_state.job_queue.append(selected_audio)
        st.experimental_rerun()


def main():
    st.header("Transcription")
    if server_state.running_file == "":
        nothing_running_view()
    else:
        something_running_view()


if __name__ == "__main__":
    with server_state_lock["running_file"]:
        if "running_file" not in server_state:
            server_state.running_file: str = ""
    with server_state_lock["progress"]:
        if "progress" not in server_state:
            server_state.progress: int = 0
    with server_state_lock["job_queue"]:
        if "job_queue" not in server_state:
            server_state.job_queue: list = []

    st_autorefresh(interval=5000)
    main()
