import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pytesseract
import fitz
from PIL import Image
import io
from fpdf import FPDF

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if not key and "GEMINI_API_KEY" in st.secrets:
    key = st.secrets["GEMINI_API_KEY"]

if key:
    try:
        genai.configure(api_key=key)
    except Exception:
        pass

def read_pdf(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    all_text = ''
    for page in doc:
        all_text += page.get_text()
    doc.close()
    try:
        file.seek(0)
    except Exception:
        pass
    return all_text.strip()

def read_ocr(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    full_text = ''
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"
    doc.close()
    try:
        file.seek(0)
    except Exception:
        pass
    return full_text.strip()

def extract_pdf_data(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    has_text = any(page.get_text().strip() for page in doc)
    doc.close()
    try:
        file.seek(0)
    except Exception:
        pass
    if has_text:
        return read_pdf(file)
    else:
        return read_ocr(file)

def analyze_resume(resume_text, operation, job_description=None):
    if not resume_text:
        return ""
    if operation == 'summarize pdf':
        base_prompt = f"""
You are an expert at summarizing documents. I will provide the full extracted text of a PDF file. Your job is to create a clear and concise summary that captures the key points, important details, and overall purpose of the document.

Rules:
- Keep it concise and easy to understand.
- Use bullet points if appropriate.
- Preserve important names, dates, numbers, or facts.
- Remove any irrelevant or repetitive content.

Here is the PDF text:
{resume_text}
"""
        if job_description:
            base_prompt += f"\nAdditional context for the summary:\n{job_description}\n"
    else:
        base_prompt = f"""
You are an experienced HR with technical experience. Your task is to review the provided resume and:
- Evaluate alignment to the chosen role.
- List existing skills and suggest missing/important skills.
- Highlight strengths and weaknesses.
- Provide a short rating out of 10.

Resume:
{resume_text}
"""
        if job_description:
            base_prompt += f"\nAdditional job description/context:\n{job_description}\n"
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(base_prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Error calling Gemini API: {e}]"

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, stripped.strip("*"))
            pdf.set_font("Arial", "", 12)
        else:
            parts = []
            temp = stripped
            while temp:
                idx_double = temp.find("**")
                idx_single = temp.find("*")
                if idx_double == -1 and idx_single == -1:
                    parts.append((temp, False))
                    break
                if idx_double != -1 and (idx_single == -1 or idx_double < idx_single):
                    if idx_double > 0:
                        parts.append((temp[:idx_double], False))
                    temp = temp[idx_double+2:]
                    end_idx = temp.find("**")
                    if end_idx == -1:
                        parts.append(("**" + temp, False))
                        break
                    parts.append((temp[:end_idx], True))
                    temp = temp[end_idx+2:]
                else:
                    if idx_single > 0:
                        parts.append((temp[:idx_single], False))
                    temp = temp[idx_single+1:]
                    end_idx = temp.find("*")
                    if end_idx == -1:
                        parts.append(("*" + temp, False))
                        break
                    parts.append((temp[:end_idx], True))
                    temp = temp[end_idx+1:]
            for text_part, is_bold in parts:
                if is_bold:
                    pdf.set_font("Arial", "B", 12)
                else:
                    pdf.set_font("Arial", "", 12)
                pdf.write(8, text_part)
            pdf.ln()
    return pdf.output(dest='S').encode('latin1')

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("AI PDF Analyzer")
st.write("Analyze your resume and summarize long pdfs with AI")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your document (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("More context:", placeholder="Paste the additional description here...")

if uploaded_file is None:
    st.warning("Please upload a file in PDF format.")
else:
    st.success("PDF uploaded successfully!")

if uploaded_file:
    operation = st.selectbox("What would you like to do:", ['summarize pdf','evaluate resume'])
    resume_text = extract_pdf_data(uploaded_file)
else:
    resume_text = ""

if 'summary_text' not in st.session_state:
    st.session_state['summary_text'] = ''

if st.button('Analyze'):
    if not uploaded_file:
        st.error('Please upload a PDF file before analyzing.')
    else:
        with st.spinner('Analyzing...'):
            analysis = analyze_resume(resume_text, operation, job_description)
            st.write(analysis)
            st.session_state['summary_text'] = analysis
            if analysis.startswith('[Error calling Gemini'):
                st.error(analysis)
            else:
                st.success('Analysis complete!')
                

summary = st.text_area('Enter your summary:', key='summary_text', height=200)

if st.button('Generate PDF'):
    text_to_pdf = st.session_state.get('summary_text', '')
    if text_to_pdf.strip():
        pdf_bytes = create_pdf(text_to_pdf)
        st.download_button(
            label='📄 Download Summary as PDF',
            data=pdf_bytes,
            file_name='summary.pdf',
            mime='application/pdf'
        )
    else:
        st.warning('Please enter some text to generate a PDF.')