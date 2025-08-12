

# JOYPDF

JOYPDF is a Streamlit web application that allows users to upload PDF documents, analyze their contents using Google Gemini AI, and generate concise summaries in professionally-styled PDF format. The app streamlines the process of extracting insights from PDFs and presenting them in a clean, readable way.

## Features

- **PDF Upload:** Easily upload PDF files for analysis.
- **AI-Based Text Analysis:** Utilizes Google Gemini AI for advanced document understanding and summarization.
- **Markdown-to-PDF Conversion:** Converts AI-generated summaries (in Markdown) into downloadable PDF files.
- **Professional PDF Styling:** Outputs summaries in clean, professional PDF layouts.
- **Robust Error Handling:** Handles file errors, API failures, and invalid inputs gracefully.

## Tech Stack

- **Python**
- **Streamlit**
- **Google Generative AI API (Gemini)**
- **PyMuPDF**
- **markdown**
- **xhtml2pdf**

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/JOYPDF.git
   cd JOYPDF
   ```
2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API Key:**
   - Create a `.env` file in the project root.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Usage

1. **Run the Streamlit app:**
   ```bash
   streamlit run app4.py
   ```
2. **Interact with the App:**
   - Upload a PDF file via the web interface.
   - The app will analyze the content using Gemini AI.
   - View and download the AI-generated summary as a PDF.

## Deployment

- The app can be deployed to [Streamlit Cloud](https://streamlit.io/cloud).
- Ensure that `requirements.txt` contains only the necessary dependencies for a minimal, fast deployment.
- Set up environment variables (e.g., `GEMINI_API_KEY`) in the Streamlit Cloud dashboard.

## Project Structure

Example file structure:
```
JOYPDF/
├── app4.py
├── requirements.txt
├── readme.md
├── .env
|── ...
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them.
4. Push to your fork and open a pull request.

