import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_waveform_plot(is_for_pdf=False):
    """Generates continuous signal audio wave plots matching the design specs."""
    fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#FFFFFF' if is_for_pdf else '#0E1117')
    ax.set_facecolor('#FFFFFF' if is_for_pdf else '#0E1117')

    t = np.linspace(0, 35, 1000)
    signal = np.sin(0.4 * t) * np.cos(3 * t) * np.sin(7 * t) + np.random.normal(0, 0.1, 1000)
    signal = np.clip(signal, -0.9, 0.9)

    ax.plot(t, signal, color='#1E88E5' if is_for_pdf else '#2563EB', alpha=0.9, linewidth=1.0)
    ax.set_title("Audio Waveform", color='black' if is_for_pdf else '#94A3B8', fontsize=10)
    ax.grid(True, color='#E2E8F0' if is_for_pdf else '#333333', alpha=0.4)
    plt.tight_layout()

    if is_for_pdf:
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        return buf
    return fig

def render_dashboard_results(m):
    """
    Renders the results dashboard using real metrics from analysis_engine.
    similarity/confidence are 0-100 scores; filler ratio/pause ratio are
    0-1 fractions.
    """
    st.markdown(f"""
        <style>
        .results-card {{ background-color: #0F172A; border: 1px solid #1E293B; padding: 25px; border-radius: 10px; margin-top: 20px; }}
        .status-banner {{ background-color: #064E3B; color: #34D399; padding: 8px 15px; border-radius: 5px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 20px; }}
        .section-header {{ font-size: 22px; font-weight: bold; color: #FFFFFF; margin-bottom: 15px; }}
        .body-text {{ font-size: 14px; color: #94A3B8; line-height: 1.7; }}
        .feedback-text {{ font-size: 13px; color: #CBD5E1; line-height: 1.6; margin-top: 10px; font-style: italic; }}
        .score-big {{ font-size: 36px; font-weight: bold; color: #FFFFFF; margin-top: 5px; }}
        .rating-text {{ font-size: 20px; font-weight: bold; color: #F59E0B; margin-top: 15px; }}
        </style>

        <div class="results-card">
            <div class="status-banner">Analysis Completed</div>
            <div style="display: flex; justify-content: space-between; gap: 20px;">
                <div style="flex: 1.3;">
                    <div class="section-header">Transcribed Explanation</div>
                    <div class="body-text">{m['transcript']}</div>
                    <div class="feedback-text">{m.get('feedback', '')}</div>
                </div>
                <div style="flex: 0.7; border-left: 1px solid #1E293B; padding-left: 25px;">
                    <div class="section-header">Final Evaluation</div>
                    <div style="color: #94A3B8; font-size: 14px;">Understanding Score</div>
                    <div class="score-big">{m['final_score']}</div>
                    <div class="rating-text">{m['understanding_level']}</div>
                </div>
            </div>
            <hr style="border-color: #1E293B; margin: 25px 0;">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div style="color: #94A3B8; font-size: 13px;">Semantic Similarity</div>
                    <div style="font-size: 24px; font-weight: bold; color: white; margin-top: 5px;">{m['semantic_similarity']}%</div>
                </div>
                <div>
                    <div style="color: #94A3B8; font-size: 13px;">Filler Word Ratio</div>
                    <div style="font-size: 24px; font-weight: bold; color: white; margin-top: 5px;">{m['filler_word_ratio']}</div>
                </div>
                <div>
                    <div style="color: #94A3B8; font-size: 13px;">Pause Ratio</div>
                    <div style="font-size: 24px; font-weight: bold; color: white; margin-top: 5px;">{m['pause_ratio']}</div>
                </div>
                <div>
                    <div style="color: #94A3B8; font-size: 13px;">Confidence</div>
                    <div style="font-size: 24px; font-weight: bold; color: white; margin-top: 5px;">{m['confidence']}%</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def compile_pdf_report(metrics, reference_text):
    """Constructs structured tabular PDF asset layout dynamically using the passed metrics dictionary."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'))
    h2_style = ParagraphStyle('SecHeader', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#1E293B'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#334155'))

    story.append(Paragraph("Voice-Based Concept Understanding Evaluation Report", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Reference Concept", h2_style))
    story.append(Paragraph(reference_text, body_style))

    story.append(Paragraph("Student Transcription", h2_style))
    story.append(Paragraph(metrics.get('transcript', 'No transcript recorded.'), body_style))

    story.append(Paragraph("Feedback", h2_style))
    story.append(Paragraph(metrics.get('feedback', 'No feedback available.'), body_style))

    story.append(Paragraph("Audio Visualization", h2_style))
    img_data = generate_waveform_plot(is_for_pdf=True)
    story.append(Image(img_data, width=480, height=120))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Evaluation Summary", h2_style))

    table_rows = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style)],
        [Paragraph("Semantic Similarity", body_style), Paragraph(f"{metrics.get('semantic_similarity', 0.0)}%", body_style)],
        [Paragraph("Filler Word Ratio", body_style), Paragraph(str(metrics.get('filler_word_ratio', 0.0)), body_style)],
        [Paragraph("Pause Ratio", body_style), Paragraph(str(metrics.get('pause_ratio', 0.0)), body_style)],
        [Paragraph("Speaking Rate (WPM)", body_style), Paragraph(str(metrics.get('speaking_rate', 0.0)), body_style)],
        [Paragraph("Confidence", body_style), Paragraph(f"{metrics.get('confidence', 0.0)}%", body_style)],
        [Paragraph("Final Score", body_style), Paragraph(f"<b>{metrics.get('final_score', '0/100')}</b>", body_style)],
        [Paragraph("Understanding Level", body_style), Paragraph(f"<b>{metrics.get('understanding_level', 'N/A')}</b>", body_style)]
    ]
    t = Table(table_rows, colWidths=[240, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#E2E8F0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
