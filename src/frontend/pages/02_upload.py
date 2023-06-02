import os
import random

import streamlit as st

from backend.file.file_manager import FileManager

# To refresh the web when file uploaded.
if "upload_key" not in st.session_state:
    st.session_state.upload_key: str = str(random.randint(1000, 100000000))

st.write("Upload your audio here.")
uploaded_files = st.file_uploader(
    "Choose a file",
    type=["m4a", "mp3"],
    accept_multiple_files=True,
    key=st.session_state.upload_key,
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_details = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": uploaded_file.size,
        }
        st.write(file_details)

    upload_btn = st.button("upload")
    if upload_btn:
        for uploaded_file in uploaded_files:
            FileManager.save_audio(uploaded_file.name, uploaded_file.getbuffer())
        st.session_state.upload_key = str(random.randint(1000, 100000000))
        st.experimental_rerun()

search_text = st.text_input("Search bar")

if search_text:
    file_paths = FileManager.get_upload_files(search_text, abs_path=True)
else:
    file_paths = FileManager.get_upload_files(abs_path=True)

for file_path in file_paths:
    filename = os.path.split(file_path)[-1]
    col1, col2 = st.columns(2)
    with col1:
        st.write(filename)
    with col2:
        if st.button("delete", key="delete" + filename):
            FileManager.delete_file(file_path)
            st.experimental_rerun()
