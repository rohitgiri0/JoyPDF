import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
# import pytesseract
import fitz
# from PIL import Image
# import io
import markdown
from xhtml2pdf import pisa

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
if not key and "GEMINI_API_KEY" in st.secrets:
    key = st.secrets["GEMINI_API_KEY"]

if not key:
    st.error("GEMINI_API_KEY is not set. Please set the API key to use this app.")
else:
    try:
        genai.configure(api_key=key)
    except Exception:
        pass

@st.cache_data
def extract_pdf_data(file):
    try:
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
            return st.error("Can Not Process OCR PDFs")
    except fitz.FileDataError:
        return "Error: Invalid or corrupted PDF file."
    except Exception as e:
        return f"Error processing PDF: {e}"

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

# def read_ocr(file):
#     pdf_bytes = file.read()
#     doc = fitz.open(stream=pdf_bytes, filetype='pdf')
#     full_text = ''
#     for page_num in range(len(doc)):
#         pix = doc[page_num].get_pixmap(dpi=300)
#         img = Image.open(io.BytesIO(pix.tobytes("png")))
#         text = pytesseract.image_to_string(img)
#         full_text += text + "\n"
#     doc.close()
#     try:
#         file.seek(0)
#     except Exception:
#         pass
#     return full_text.strip()

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
    elif operation=='evaluate resume':
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
    elif operation=='Solve Assignment':
        base_prompt = f"""
        You are a knowledgeable and detail-oriented academic assistant.
        Your task is to carefully read the provided assignment text and produce clear, complete, and well-structured solutions.

        Rules:
        - Answer all parts of the assignment thoroughly.
        - Use clear formatting: headings, bullet points, or numbered lists where applicable.
        - Keep the tone formal and academic.

        Assignment Text:
        {resume_text}
        """
        if job_description:
            base_prompt += f"\nAdditional information for solutions\n{job_description}\n"
    else:
        st.warning("please choose a valid operation!")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(base_prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Error calling Gemini API: {e}]"

from io import BytesIO

def create_pdf(md_text):
    html_content = markdown.markdown(md_text)

    # wrapped markdown in html for better readability
    
    html_full = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; font-size: 16px; }}
        h1, h2, h3 {{ color: #2C3E50; }}
        ul {{ margin-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        strong {{ color: #34495E; font-weight: bold; }}
    </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generating pdf into memory
    pdf_buffer = BytesIO()
    try:
        pisa_status = pisa.CreatePDF(html_full, dest=pdf_buffer)
        if pisa_status.err:
            return None
        return pdf_buffer.getvalue()
    except Exception:
        return None

st.set_page_config(page_title="JoyPDF",page_icon='📄', layout="wide")
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
    try:
        operation = st.selectbox("What would you like to do:", ['summarize pdf','evaluate resume','Solve Assignment'])
        resume_text = extract_pdf_data(uploaded_file)
    except Exception:
        resume_text= "I can not process OCR(image scanned pdfs)"
        st.error("Can Not process OCR pdfs")
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
            print(analysis)
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
        if pdf_bytes is None:
            st.error('Failed to generate PDF. Please try again.')
        else:
            st.download_button(
                label='📄 Download Summary as PDF',
                data=pdf_bytes,
                file_name='summary.pdf',
                mime='application/pdf'
            )
    else:
        st.warning('Please enter some text to generate a PDF.')