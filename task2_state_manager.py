import streamlit as st

def init_session_state():
    """Safeguards user tracking data models across Streamlit re-run evaluation cycles."""
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "metrics" not in st.session_state:
        st.session_state.metrics = {}
    if "previous_file_name" not in st.session_state:
        st.session_state.previous_file_name = None
    if "analysis_error" not in st.session_state:
        st.session_state.analysis_error = None

def validate_uploaded_audio(uploaded_file):
    """Executes validation checks to catch corrupted or unsupported audio assets early."""
    if uploaded_file is None:
        return False

    # Reset application state automatically if a completely new file is introduced
    if st.session_state.previous_file_name != uploaded_file.name:
        st.session_state.analysis_complete = False
        st.session_state.metrics = {}
        st.session_state.analysis_error = None
        st.session_state.previous_file_name = uploaded_file.name

    if uploaded_file.size == 0:
        st.error("❌ Operational Failure: The uploaded file contains no data or is corrupted.")
        return False

    if not (uploaded_file.name.endswith('.wav') or uploaded_file.name.endswith('.mp3')):
        st.error("❌ Format Failure: Unsupported file extension type. Provide standard WAV or MP3 audio.")
        return False

    return True

if __name__ == "__main__":
    st.set_page_config(page_title="VBCUA - Task 2", layout="wide")
    init_session_state()
    st.info("State Management Subsystem active and initialized.")
