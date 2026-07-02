import streamlit as st

# Import your layout tasks
from task1_ui_layout import render_header_and_layout
from task2_state_manager import init_session_state, validate_uploaded_audio
from task3_output_engine import render_dashboard_results, compile_pdf_report, generate_waveform_plot
from analysis_engine import run_real_analysis, AnalysisPipelineError
from config import REFERENCE_CONCEPT_TEXT

# =====================================================================
# 🎮 MAIN APPLICATION CONTROLLER
# =====================================================================
def main():
    st.set_page_config(page_title="VBCUA", page_icon="🎤", layout="wide")

    # Initialize the state models tracking (Task 2)
    init_session_state()

    # Render layout columns (Task 1)
    uploaded_file = render_header_and_layout()

    if uploaded_file is not None:
        # Validate file integrity safely (Task 2)
        if validate_uploaded_audio(uploaded_file):
            st.audio(uploaded_file, format="audio/wav")

            # Action Evaluation Button Block
            if not st.session_state.analysis_complete:
                if st.button("Analyze Concept Understanding", type="primary"):
                    with st.spinner("Transcribing audio, scoring understanding, and analyzing fluency..."):
                        try:
                            st.session_state.metrics = run_real_analysis(
                                uploaded_file, reference_text=REFERENCE_CONCEPT_TEXT
                            )
                            st.session_state.analysis_complete = True
                            st.session_state.analysis_error = None
                        except AnalysisPipelineError as exc:
                            st.session_state.analysis_complete = False
                            st.session_state.analysis_error = str(exc)
                    st.rerun()

            # Surface a clear error instead of silently showing fake results
            if st.session_state.get("analysis_error"):
                st.error(f"❌ Analysis failed: {st.session_state.analysis_error}")

            # Render Results Dashboard & PDF download buttons (Task 3)
            if st.session_state.analysis_complete:
                m = st.session_state.metrics

                # Render results dark box container panel
                render_dashboard_results(m)

                # Build dynamic PDF report
                pdf_data = compile_pdf_report(m, reference_text=REFERENCE_CONCEPT_TEXT)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"Evaluation_Report_{uploaded_file.name}.pdf",
                    mime="application/pdf"
                )

                # Draw live waveform plot window
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📊 Waveform Visualizations")
                st.pyplot(generate_waveform_plot(is_for_pdf=False))
    else:
        st.info("Upload an audio file to begin analysis.")


if __name__ == "__main__":
    main()
