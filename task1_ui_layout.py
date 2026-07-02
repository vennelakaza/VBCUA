import streamlit as st

from config import REFERENCE_CONCEPT_TITLE, REFERENCE_CONCEPT_TEXT

def render_header_and_layout():
    """Renders the top branding header and establishes the two-column grid structure."""
    # Custom CSS Injector for Dark-Theme UI Consistency
    st.markdown("""
        <style>
        .main-title { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
        .subtitle { font-size: 16px; color: #A0A0A0; margin-bottom: 25px; }
        .concept-box { background-color: #1E1E1E; padding: 20px; border-radius: 8px; border: 1px solid #333333; }
        .concept-title { font-size: 20px; font-weight: bold; color: #FFFFFF; margin-bottom: 10px; }
        .concept-body { font-size: 14px; color: #D0D0D0; line-height: 1.6; }
        </style>
    """, unsafe_allow_html=True)

    # App Header branding block
    st.markdown('<div class="main-title">Voice-Based Concept Understanding Analyser</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Automated evaluation of spoken conceptual explanations using AI.</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Establishing presentation side-by-side columns
    col1, col2 = st.columns([1.2, 0.8], gap="large")

    with col1:
        st.subheader("Upload Student Audio (WAV)")
        uploaded_file = st.file_uploader(
            "Drag and drop file here",
            type=["wav", "mp3"],
            help="Limit 200MB per file • WAV, MP3"
        )

    with col2:
        st.markdown(
            f"""
            <div class="concept-box">
                <div class="concept-title">Concept Reference: {REFERENCE_CONCEPT_TITLE}</div>
                <div class="concept-body">{REFERENCE_CONCEPT_TEXT}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    return uploaded_file

if __name__ == "__main__":
    st.set_page_config(page_title="VBCUA - Task 1", layout="wide")
    uploaded_file = render_header_and_layout()
    if uploaded_file is None:
        st.info("Upload an audio file to begin analysis.")
