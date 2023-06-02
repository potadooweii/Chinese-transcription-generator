import os

import streamlit as st

from backend.file.file_manager import FileManager

search_text = st.text_input("Search bar")

if search_text:
    file_paths = FileManager.get_download_files(search_text, abs_path=True)
else:
    file_paths = FileManager.get_download_files(abs_path=True)

for file_path in file_paths:
    filename = os.path.split(file_path)[-1]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(filename)
    with col2:
        with open(file_path) as f:
            st.download_button("download", f, key="download" + filename)
    with col3:
        if st.button("delete", key="delete" + filename):
            FileManager.delete_file(file_path)
            st.experimental_rerun()
