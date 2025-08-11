import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pytesseract
from google import genai
import fitz
from PIL import Image
import io

load_dotenv()
key=os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=key)


def read_pdf(file):
    try:
        pdf_bytes=file.read()
        doc=fitz.open(stream=pdf_bytes,filetype='pdf')
        all_text=''
        for page in doc:
            all_text+=page.get_text()
        return all_text
    except Exception as e:
        st.text("Some error occured")
        print("Some error occured")
def read_ocr(file):
    try:
        doc=fitz.open(file)
        full_text=''
        for page in range(len(doc)):
            pix=doc[page].get_pixmap(dpi=300)
            img=Image.open(io.BytesIO(pix.tobytes("png")))
            text=pytesseract.image_to_string(img)
            full_text+=text+'\n'
        return full_text
    except Exception as e:
        st.text("Some error occured")
        print("Some error occured")

def extract_pdf_data(file):
    try:
        pdf_bytes=file.read()
        doc=fitz.open(stream=pdf_bytes,filetype='pdf')
        has_text=any(page.get_text().strip() for page in doc)
        file.seek(0)
        if has_text:
            return read_pdf(file)
        else:
            return read_ocr(file)
    except Exception as e:
        st.text("Some error occured")
        print("Some error occured")



# function to get response from Gemini AI
def analyze_resume(resume_text, operation,job_description=None):

    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    if operation=='summarize pdf':
        base_prompt=f"""
        You are an expert at summarizing documents. 
        I will provide the full extracted text of a PDF file. 
        Your job is to create a clear and concise summary that captures the key points, 
        important details, and overall purpose of the document.

        Rules:
        - Keep it consise and easy to understand.
        - Use bullet points if appropriate.
        - Use tables if needed
        - Preserve important names, dates, numbers, or facts.
        - Remove any irrelevant or repetitive content.

        Here is the PDF text:
        {resume_text}
        """
        if job_description:
            base_prompt += f"""
            Additionally:
            {job_description}
            """
    else:
        base_prompt = f"""
        You are an experienced HR with Technical Experience in the field of any one job role from Data Science, Data Analyst, DevOPS, Machine Learning Engineer, Prompt Engineer, AI Engineer, Full Stack Web Development, Big Data Engineering, Marketing Analyst, Human Resource Manager, Software Developer your task is to review the provided resume.
        Please share your professional evaluation on whether the candidate's profile aligns with the role.ALso mention Skills he already have and suggest some skills to imorve his resume. Highlight the strengths and weaknesses keep it consise and format the text very well add line spaces and make it look better,formatted overall. at last give it a rating out of 10.

        Resume:
        {resume_text}
        """

        if job_description:
            base_prompt += f"""
            Additional, description:
            
            {job_description}
            """

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=base_prompt
    )

    analysis = response.text.strip()
    return analysis

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("AI PDF Analyzer")
st.write("Analyze your resume and summarize long pdfs with Ai")

col1 , col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Enter Job Description:", placeholder="Paste the additional description here...")

if uploaded_file is not None:
    st.success("pdf uploaded successfully!")
else:
    st.warning("Please upload a file in PDF format.")


st.markdown("<div style= 'padding-top: 10px;'></div>", unsafe_allow_html=True)
if uploaded_file:
    operation=st.selectbox("what would you like to do: ",['evaluate resume','summarize pdf'])
    # saving uploaded document loacally
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    # extracting text
    resume_text = extract_pdf_data(uploaded_file)

    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            try:
                # analyze resume
                analysis = analyze_resume(resume_text, operation,job_description)
                st.success("Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

