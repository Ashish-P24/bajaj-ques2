import os
import streamlit as st
from modules.extractor import extract_text_from_file
from modules.embedder import get_faiss_index, get_top_chunks
from modules.llm import llm_extract_answer # Ensure this is correct, previously was query_parser.py

# App setup
st.set_page_config(page_title="DocuQuery", layout="wide")

# Title and tagline
st.markdown(
    "<h1 style='display: inline;'>DocuQuery</h1> "
    "<span style='color: gray; font-size: 1.2em;'>— Smart Inspection, Smarter Answers.</span>",
    unsafe_allow_html=True
)

# Info icon
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    Upload Document: Start by uploading your PDF, DOCX, CSV, or XLSX file.

Ask a Question: Once processed, type your question about the document's content.

Get Instant Answers: DocuQuery's AI will provide a precise answer based on your document.

Refine Results (Optional): Use the sidebar settings to adjust AI temperature or view source chunks.

Download History (Optional): Export your Q&A session as PDF or JSON anytime.
    """)

# Sidebar configuration
st.sidebar.header("Settings")
# LLM Temperature will be read directly when the answer is requested
temperature = st.sidebar.slider("LLM Temperature", 0.0, 1.0, 0.5, 0.1, key="llm_temp_slider")

cleanup_answer = st.sidebar.checkbox("Cleanup Answer Formatting", True, key="cleanup_checkbox")
show_chunks = st.sidebar.checkbox("Show Matching Chunks", False, key="show_chunks_checkbox")

# Session state setup
if "file" not in st.session_state:
    st.session_state.file = None
if "all_text" not in st.session_state:
    st.session_state.all_text = ""
if "index" not in st.session_state:
    st.session_state.index = None
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "query" not in st.session_state: # Added for clearing the input box
    st.session_state.query = ""
if "last_uploaded_file_name" not in st.session_state: # To prevent re-processing same file
    st.session_state.last_uploaded_file_name = None
if "last_uploaded_file_size" not in st.session_state: # To prevent re-processing same file
    st.session_state.last_uploaded_file_size = None


# File upload
file = st.file_uploader("Upload a document", type=["pdf", "docx", "csv", "xlsx"])
if file:
    st.session_state.file = file
    # Only re-process if a new file is uploaded or the file content changes
    if st.session_state.last_uploaded_file_name != file.name or \
       st.session_state.last_uploaded_file_size != file.size:
        with st.spinner("Processing document... This may take a moment."):
            st.session_state.all_text = extract_text_from_file(file)
            st.session_state.index = get_faiss_index(st.session_state.all_text)
        st.success("✅ Document processed successfully.")
        st.session_state.last_uploaded_file_name = file.name
        st.session_state.last_uploaded_file_size = file.size
    else:
        st.info("File already loaded. No need to re-process.")

# User question input
# Use a key and default to st.session_state.query for controlled input
query = st.text_input("Ask a question about the document:", value=st.session_state.query, key="query_input")

# Handle Q&A only when a button is clicked and an index exists
if st.button("Get Answer"):
    if st.session_state.index:
        if query: # Ensure query is not empty
            st.session_state.query = query # Store the current query before clearing
            
            with st.spinner("Getting answer..."):
                matched_chunks = get_top_chunks(st.session_state.index, query, st.session_state.all_text)
                context = "\n\n".join(matched_chunks)
                
                # Pass the temperature from the slider
                answer = llm_extract_answer(context, query, temperature=st.session_state.llm_temp_slider) 

                if st.session_state.cleanup_checkbox: # Use session state for checkbox
                    answer = answer.replace("\n", " ").strip()

            # Display answer
            st.markdown("### 📘 Answer")
            st.write(answer)

            # Show chunks
            if st.session_state.show_chunks_checkbox: # Use session state for checkbox
                with st.expander("🧩 Matching Chunks"):
                    for chunk in matched_chunks:
                        st.markdown(f"- {chunk}")

            # Save Q&A
            st.session_state.qa_history.append({"question": query, "answer": answer})
            st.session_state.query = "" # Clear the input box after submission
            st.rerun() # Rerun to clear the input box immediately
        else:
            st.warning("Please enter a question.")
    else:
        st.warning("Please upload a document first.")


# Show Q&A history
if st.session_state.qa_history:
    st.markdown("### 🕘 Previous Q&A")
    # Display in reverse chronological order
    for i, qa in enumerate(reversed(st.session_state.qa_history), 1):
        st.markdown(f"**Q:** {qa['question']}")
        st.markdown(f"**A:** {qa['answer']}")
        st.markdown("---")

    # Export buttons
    import json
    from fpdf import FPDF # Make sure fpdf is in your requirements.txt

    if st.button("📄 Download Q&A as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Add a title to the PDF
        pdf.multi_cell(0, 10, "DocuQuery Q&A History\n\n", align='C')
        
        for i, qa in enumerate(st.session_state.qa_history, 1):
            pdf.multi_cell(0, 10, f"Q{i}: {qa['question']}\n", align='L')
            pdf.multi_cell(0, 10, f"A{i}: {qa['answer']}\n\n", align='L')
        
        pdf_path = "qa_history.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Click to download PDF", f, file_name="qa_history.pdf")

    if st.button("🧾 Download Q&A as JSON"):
        json_data = json.dumps(st.session_state.qa_history, indent=2)
        st.download_button("⬇️ Click to download JSON", json_data, file_name="qa_history.json")