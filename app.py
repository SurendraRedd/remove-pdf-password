# app.py
# PDF Password Remover ────────────────────────────────────────────────────────
# A simple Streamlit app to remove known passwords from PDF files

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import time
import math
import re
import json
from datetime import datetime
import streamlit.components.v1 as components

# Optional: better preview
try:
    import fitz  # PyMuPDF
    HAS_FITZM = True
except ImportError:
    HAS_FITZM = False

# ──── CONSTANTS ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 150
WARN_FILE_SIZE_MB = 80
DEFAULT_DPI = 120
PREVIEW_WIDTH = 700
CONTACT_LOG_FILE = "contact_submissions.json"

st.set_page_config(
    page_title="PDF Unlocker",
    page_icon="🔓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ──── UTILITY FUNCTIONS ─────────────────────────────────────────────────────
def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def save_contact_submission(name: str, email: str, subject: str, message: str) -> bool:
    """Save contact form submission to JSON file."""
    try:
        submission = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }
        
        submissions = []
        if os.path.exists(CONTACT_LOG_FILE):
            try:
                with open(CONTACT_LOG_FILE, "r") as f:
                    submissions = json.load(f)
            except (json.JSONDecodeError, IOError):
                submissions = []
        
        submissions.append(submission)
        
        with open(CONTACT_LOG_FILE, "w") as f:
            json.dump(submissions, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving submission: {str(e)}")
        return False

def format_file_size(size_bytes: int) -> float:
    """Convert bytes to MB with precision."""
    return size_bytes / 1_048_576

def get_generated_filename(original_name: str) -> str:
    """Generate clean output filename."""
    base, ext = os.path.splitext(original_name)
    return f"{base} - unlocked{ext}"

# ──── TITLE & DESCRIPTION ───────────────────────────────────────────────────
st.title("🔓 PDF Unlocker")
st.markdown("Remove password protection from your PDF files (when you know the password).")

st.caption("Only works with files you own or have permission to process.")

# ──── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("PDF Unlocker")
    st.markdown("""
    **Features**
    - Remove user or owner password
    - First-page preview (if PyMuPDF installed)
    - Clean filename suggestions
    - Size & memory warnings

    **Limitations**
    - Does **not** remove printing/copying restrictions
    - Very large files (>100–150 MB) may fail
    - Some exotic encryption methods are not supported
    """)

    st.markdown("---")

    st.markdown("**Recommended install**")
    st.code("pip install streamlit PyPDF2 pymupdf pycryptodome", language="bash")

    st.caption("Made with Streamlit • PyPDF2 • (optional) PyMuPDF")

# ──── HOW TO USE SECTION ────────────────────────────────────────────────────
with st.expander("📖 How to Use This Tool", expanded=False):
    st.markdown("""
    ### Step-by-Step Guide
    
    1. **Prepare Your PDF**
       - Ensure you have the password for the file
       - Save it to a secure location
    
    2. **Upload Your File**
       - Click "Upload your password-protected PDF"
       - Select a single PDF file (up to 150 MB recommended)
    
    3. **Enter Your Password**
       - In the password field, enter the correct password
       - Password is **case-sensitive**
       - Your password is not stored anywhere
    
    4. **Click "Remove Password"**
       - The app will decrypt the file
       - Progress bar shows page processing
       - Processing time depends on file size
    
    5. **Download Your File**
       - Click "Download unlocked PDF"
       - The file will download as `[filename] - unlocked.pdf`
    
    ### 🔒 Security & Privacy
    - ✅ Files are processed locally in your browser session
    - ✅ No files are stored on our servers
    - ✅ All data is deleted after download or page refresh
    - ✅ Use HTTPS connections for added security
    
    ### ⚠️ Important Notes
    - This tool only removes password restrictions
    - It **does NOT** unlock copying/printing restrictions (owner passwords)
    - Very large files (>100 MB) may timeout
    - Ensure you own the PDF or have permission to decrypt it
    
    ### 💡 Tips & Tricks
    - Have your password ready before uploading
    - For very large PDFs, try splitting them first
    - Check file size before uploading (shows in metrics)
    - Preview feature requires PyMuPDF library
    
    ### ❓ Troubleshooting
    - **"Incorrect password"** → Double-check password (case-sensitive)
    - **"AES encryption requires PyCryptodome"** → Reinstall dependencies
    - **Processing timeout** → File is too large, try splitting it
    - **Preview not showing** → Install PyMuPDF for better support
    """)

# ──── MAIN AREA ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your password-protected PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Only single PDF files are supported at the moment"
)

if uploaded_file is not None:
    file_size_mb = format_file_size(uploaded_file.size)

    # Size feedback
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File is very large ({file_size_mb:.1f} MB) → high risk of timeout or memory error.")
        st.info(f"Maximum recommended size: {MAX_FILE_SIZE_MB} MB")
        st.stop()
    elif file_size_mb > WARN_FILE_SIZE_MB:
        st.warning(f"⚠️ Large file detected ({file_size_mb:.1f} MB). Processing may be slow.")
    else:
        st.success(f"✅ File loaded: {file_size_mb:.1f} MB", icon="✅")

    st.markdown(f"**Filename:** `{uploaded_file.name}`")

    password = st.text_input(
        "Enter the PDF password",
        type="password",
        placeholder="Case-sensitive",
        help="The password used to open or restrict the document",
        key="pdf_password"
    )

    if st.button("🔓 Remove Password", type="primary", use_container_width=True, disabled=not password.strip()):
        processing_container = st.container()
        with st.spinner("Processing PDF... Please wait"):
            start_time = time.time()
            try:
                # ─── Read file ────────────────────────────────
                pdf_bytes = uploaded_file.getvalue()
                pdf_stream = io.BytesIO(pdf_bytes)

                reader = PdfReader(pdf_stream)

                processing_container.info("Checking encryption & metadata...")

                if not reader.is_encrypted:
                    processing_container.success("This PDF is not password protected.")
                    st.info("No password was detected. You can download the file as-is.")
                else:
                    processing_container.info("Attempting to decrypt with provided password...")

                    decrypt_result = reader.decrypt(password)

                    if decrypt_result == 0:
                        processing_container.error("Decryption failed — incorrect password.")
                        st.stop()

                    status_text = {
                        1: "User password accepted (restrictions may remain)",
                        2: "Owner/full password accepted → complete unlock"
                    }.get(decrypt_result, "Decrypted")

                    processing_container.success(status_text)

                # ─── Create clean PDF with animated progress ──
                processing_container.info("Creating unprotected version...")

                writer = PdfWriter()

                total_pages = max(1, len(reader.pages))
                progress = st.progress(0)
                progress_text = st.empty()

                for i, page in enumerate(reader.pages, 1):
                    writer.add_page(page)
                    percent = math.floor(i / total_pages * 100)
                    progress.progress(percent)
                    progress_text.markdown(f"Adding page {i} of {total_pages} — {percent}%")

                try:
                    writer.add_metadata(reader.metadata or {})
                except Exception:
                    pass

                # Write to memory
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)

                end_time = time.time()
                elapsed = end_time - start_time

                progress.progress(100)
                progress_text.success("PDF creation complete")

                # ─── Filename logic & stats ───────────────────
                new_name = get_generated_filename(uploaded_file.name)

                orig_mb = format_file_size(uploaded_file.size)
                out_mb = format_file_size(len(output.getvalue()))
                pages = total_pages

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Pages", str(pages))
                c2.metric("Time", f"{elapsed:.1f}s")
                c3.metric("Original size", f"{orig_mb:.1f} MB")
                c4.metric("Unlocked size", f"{out_mb:.1f} MB")

                # ─── Download button ─────────────────────────
                st.download_button(
                    label=f"⬇️ Download unlocked PDF ({out_mb:.1f} MB)",
                    data=output,
                    file_name=new_name,
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_unlocked"
                )

                # ─── Preview (optional) ────────────────────────
                if HAS_FITZM:
                    try:
                        st.markdown("**First page preview**")
                        doc = fitz.open(stream=output.getvalue(), filetype="pdf")
                        if len(doc) >= 1:
                            pix = doc[0].get_pixmap(dpi=DEFAULT_DPI)
                            st.image(pix.tobytes("png"), width=PREVIEW_WIDTH)
                        doc.close()
                    except Exception as e:
                        st.caption(f"Preview could not be generated: {str(e)}")
                else:
                    st.caption("Install PyMuPDF (`pip install pymupdf`) to see preview")

                # ─── Fun completion animation ────────────────
                animation_html = """
                <div style='display:flex;flex-direction:column;align-items:center'>
                  <style>
                  .unlock {{
                    width:120px;height:120px;display:flex;align-items:center;justify-content:center;
                    margin:12px;
                  }}
                  .lock-body {{
                    width:72px;height:58px;background:#0ea5a4;border-radius:6px;position:relative;box-shadow:0 6px 18px rgba(0,0,0,0.12);
                  }}
                  .shackle {{
                    width:56px;height:56px;border:8px solid #0ea5a4;border-bottom:0;border-radius:36px;position:absolute;top:-46px;left:8px;transform-origin:center;
                    transform: rotate(0deg);
                    transition: transform 0.8s cubic-bezier(.2,.8,.2,1);
                  }}
                  .shackle.open {{ transform: rotate(-45deg) translate(-6px,-6px); }
                  .confetti {{position:relative;margin-top:6px;width:220px;height:40px;}}
                  .dot{width:8px;height:8px;border-radius:50%;position:absolute;opacity:0;animation:pop 1s ease forwards}
                  .dot:nth-child(1){left:10px;background:#ef4444;animation-delay:.0s}
                  .dot:nth-child(2){left:40px;background:#f59e0b;animation-delay:.05s}
                  .dot:nth-child(3){left:70px;background:#eab308;animation-delay:.1s}
                  .dot:nth-child(4){left:100px;background:#10b981;animation-delay:.15s}
                  .dot:nth-child(5){left:130px;background:#3b82f6;animation-delay:.2s}
                  .dot:nth-child(6){left:160px;background:#8b5cf6;animation-delay:.25s}
                  @keyframes pop{0%{transform:translateY(0) scale(.2);opacity:0}50%{opacity:1}100%{transform:translateY(-28px) scale(1);opacity:1}}
                  </style>
                  <div class='unlock'>
                    <div class='lock-body'></div>
                    <div id='sh' class='shackle'></div>
                  </div>
                  <div class='confetti'>
                    <div class='dot'></div><div class='dot'></div><div class='dot'></div><div class='dot'></div><div class='dot'></div><div class='dot'></div>
                  </div>
                </div>
                <script>
                  const sh = document.getElementById('sh');
                  setTimeout(()=>{ sh.classList.add('open') }, 700);
                </script>
                """

                components.html(animation_html, height=220)

            except Exception as e:
                err_msg = str(e)
                if "PyCryptodome is required" in err_msg or "PyCryptodome is required for AES algorithm" in err_msg:
                    processing_container.error("PDF uses AES encryption which requires PyCryptodome.")
                    with st.expander("Install PyCryptodome"):
                        st.markdown("Install the dependency and restart the app:")
                        st.code("pip install pycryptodome", language="bash")
                    with st.expander("Error details"):
                        st.exception(e)
                else:
                    processing_container.error("Could not process this PDF file.")
                    with st.expander("Error details"):
                        st.exception(e)

else:
    st.info("Upload a password-protected PDF file to start.", icon="📄")

st.markdown("---")

# ──── CONTACT FORM SECTION ──────────────────────────────────────────────────
st.subheader("📬 Get in Touch")
st.markdown("Have feedback, questions, or issues? We'd love to hear from you!")

with st.form("contact_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        contact_name = st.text_input(
            "Your Name",
            placeholder="John Doe",
            max_chars=100
        )
    
    with col2:
        contact_email = st.text_input(
            "Your Email",
            placeholder="john@example.com",
            max_chars=150
        )
    
    contact_subject = st.selectbox(
        "Subject",
        [
            "Bug Report",
            "Feature Request",
            "General Feedback",
            "Technical Support",
            "Other"
        ],
        index=2
    )
    
    contact_message = st.text_area(
        "Message",
        placeholder="Tell us what's on your mind...",
        height=120,
        max_chars=1000
    )
    
    submit_button = st.form_submit_button(
        "✉️ Send Message",
        use_container_width=True,
        type="secondary"
    )
    
    if submit_button:
        # Validation
        if not contact_name.strip():
            st.error("❌ Please enter your name.")
        elif not contact_email.strip():
            st.error("❌ Please enter your email.")
        elif not validate_email(contact_email):
            st.error("❌ Please enter a valid email address.")
        elif not contact_message.strip():
            st.error("❌ Please enter a message.")
        else:
            # Save submission
            if save_contact_submission(contact_name, contact_email, contact_subject, contact_message):
                st.success("✅ Thank you! Your message has been sent successfully.")
                st.balloons()
            else:
                st.error("❌ There was an error sending your message. Please try again.")

st.markdown("---")

# ──── FOOTER ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔐 **Privacy:** No data is stored on servers")
with col2:
    st.caption("⚖️ **Legal:** Use responsibly with owned files")
with col3:
    st.caption(f"📅 **Version:** {time.strftime('%Y-%m')}")

st.caption("Built with ❤️ using Streamlit • PyPDF2 • PyMuPDF")
