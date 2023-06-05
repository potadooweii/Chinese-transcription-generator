import os

import streamlit as st
from streamlit_autorefresh import st_autorefresh


from backend.file.file_manager import FileManager

def main():
    search_text = st.text_input("Search bar")

    if search_text:
        file_paths = FileManager.get_download_files(search_text, abs_path=True)
    else:
        file_paths = FileManager.get_download_files(abs_path=True)

    for file_path in file_paths:
        filename = os.path.split(file_path)[-1]
        cols = st.columns(3)
        
        with cols[0]:
            st.write(filename)
        with cols[1]:
            with open(file_path) as f:
                st.download_button(
                    "download",
                    f,
                    file_name=filename,
                    key="download" + filename
                )
        with cols[2]:
            if st.button("delete", key="delete" + filename):
                FileManager.delete_file(file_path)
                st.experimental_rerun()

if __name__ == "__main__":
    st_autorefresh(interval=5000)
    main()