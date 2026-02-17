# app.py
# PDF Password Remover ────────────────────────────────────────────────────────
# A simple Streamlit app to remove known passwords from PDF files

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import time
import math
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

st.set_page_config(
    page_title="PDF Unlocker",
    page_icon="🔓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ──── CUSTOM CSS & ANIMATIONS ──────────────────────────────────────────────
custom_css = """
<style>
/* Global Styling */
:root {
    --primary-color: #0ea5a4;
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
}

/* Gradient Background */
.main-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 20px;
}

/* Animated Title */
.title-gradient {
    background: linear-gradient(90deg, #667eea, #764ba2, #0ea5a4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 3s ease infinite;
    font-weight: bold;
}

@keyframes gradient-shift {
    0%, 100% { filter: hue-rotate(0deg); }
    50% { filter: hue-rotate(20deg); }
}

/* Floating Animation */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.float-animation {
    animation: float 3s ease-in-out infinite;
}

/* Pulse Animation */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(14, 165, 164, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(14, 165, 164, 0); }
}

.pulse-glow {
    animation: pulse-glow 2s infinite;
}

/* Slide In Animation */
@keyframes slide-in {
    from { 
        opacity: 0; 
        transform: translateX(-20px);
    }
    to { 
        opacity: 1; 
        transform: translateX(0);
    }
}

.slide-in {
    animation: slide-in 0.5s ease-out;
}

/* Rotate Animation */
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.spinner {
    animation: spin 2s linear infinite;
}

/* Bounce Animation */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.bounce {
    animation: bounce 0.6s ease-in-out;
}

/* Shimmer Loading Effect */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.shimmer-load {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

/* File Upload Hover Effect */
.upload-zone:hover {
    background: rgba(14, 165, 164, 0.1);
    border-color: #0ea5a4;
    transition: all 0.3s ease;
}

/* Smooth Button Transitions */
button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* Card Styling */
.card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(14, 165, 164, 0.2);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 8px 24px rgba(14, 165, 164, 0.15);
    transform: translateY(-4px);
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    animation: slide-in 0.5s ease-out forwards;
    opacity: 0;
}

.metric-card:nth-child(1) { animation-delay: 0s; }
.metric-card:nth-child(2) { animation-delay: 0.1s; }
.metric-card:nth-child(3) { animation-delay: 0.2s; }
.metric-card:nth-child(4) { animation-delay: 0.3s; }

/* Success Animation */
@keyframes check-mark {
    0% { 
        stroke-dasharray: 50;
        stroke-dashoffset: 50;
        opacity: 0;
    }
    100% { 
        stroke-dasharray: 50;
        stroke-dashoffset: 0;
        opacity: 1;
    }
}

.check-mark {
    animation: check-mark 0.6s ease-out;
}

/* Loading Bar Animation */
@keyframes progress-fill {
    0% { width: 0%; }
    100% { width: 100%; }
}

/* Rainbow Animation */
@keyframes rainbow {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
}

.rainbow {
    animation: rainbow 3s linear infinite;
}

/* Fade In Animation */
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

.fade-in {
    animation: fade-in 0.6s ease-out;
}

/* Scale Animation */
@keyframes scale-pop {
    0% { transform: scale(0.8); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.scale-pop {
    animation: scale-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
</style>
"""

components.html(custom_css, height=0)

# ──── UTILITY FUNCTIONS ─────────────────────────────────────────────────────
def format_file_size(size_bytes: int) -> float:
    """Convert bytes to MB with precision."""
    return size_bytes / 1_048_576

def get_generated_filename(original_name: str) -> str:
    """Generate clean output filename."""
    base, ext = os.path.splitext(original_name)
    return f"{base} - unlocked{ext}"

def animated_title():
    """Display animated title with gradient effect."""
    title_html = """
    <div style='text-align: center; padding: 30px 0;'>
        <div class='title-gradient float-animation' style='font-size: 48px; letter-spacing: 2px;'>
            🔓 PDF UNLOCKER
        </div>
        <div style='font-size: 16px; color: #666; margin-top: 10px; animation: fade-in 1.5s ease-out;'>
            ✨ Unlock your password-protected PDFs instantly
        </div>
    </div>
    """
    components.html(title_html, height=100)

def animated_upload_indicator():
    """Show animated upload indicator."""
    upload_html = """
    <div style='text-align: center; margin: 20px 0;'>
        <div class='float-animation' style='font-size: 40px;'>📄</div>
        <div style='color: #0ea5a4; font-weight: bold; margin-top: 8px; animation: fade-in 0.8s;'>
            Ready to Upload
        </div>
    </div>
    """
    components.html(upload_html, height=80)

def processing_animation():
    """Show processing animation."""
    processing_html = """
    <div style='text-align: center; padding: 20px;'>
        <div class='spinner' style='font-size: 48px; display: inline-block;'>⚙️</div>
        <div style='margin-top: 15px; color: #0ea5a4; font-weight: bold; animation: fade-in 0.8s;'>
            Processing your PDF...
        </div>
        <div class='shimmer-load' style='height: 6px; border-radius: 3px; margin-top: 15px;'></div>
    </div>
    """
    components.html(processing_html, height=100)

def success_animation():
    """Show success animation."""
    success_html = """
    <div style='text-align: center; padding: 30px;'>
        <div class='scale-pop float-animation' style='font-size: 60px; display: inline-block; animation: scale-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);'>
            🎉
        </div>
        <div style='margin-top: 20px; font-size: 18px; color: #10b981; font-weight: bold; animation: slide-in 0.8s ease-out 0.3s both;'>
            PDF Successfully Unlocked!
        </div>
    </div>
    """
    components.html(success_html, height=120)

# ──── TITLE & DESCRIPTION ───────────────────────────────────────────────────
animated_title()

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
st.markdown("<br>", unsafe_allow_html=True)

# Show upload indicator
animated_upload_indicator()

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
        # Show processing animation
        processing_animation()
        
        processing_container = st.container()
        with st.spinner(""):
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

                # Show success animation
                success_animation()

                # Display metrics with animation
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📊 Processing Summary", divider="rainbow")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Pages", str(pages))
                with col2:
                    st.metric("⏱️ Time", f"{elapsed:.1f}s")
                with col3:
                    st.metric("📥 Original", f"{orig_mb:.1f} MB")
                with col4:
                    st.metric("📤 Unlocked", f"{out_mb:.1f} MB")

                # ─── Download button ─────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
                with download_col2:
                    st.download_button(
                        label="✨ Download Unlocked PDF ✨",
                        data=output,
                        file_name=new_name,
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_unlocked"
                    )

                # ─── Preview (optional) ────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                if HAS_FITZM:
                    try:
                        with st.expander("👁️ View First Page Preview", expanded=True):
                            doc = fitz.open(stream=output.getvalue(), filetype="pdf")
                            if len(doc) >= 1:
                                pix = doc[0].get_pixmap(dpi=DEFAULT_DPI)
                                preview_col1, preview_col2, preview_col3 = st.columns([1, 1, 1])
                                with preview_col2:
                                    st.image(pix.tobytes("png"), width=PREVIEW_WIDTH, use_column_width=True)
                            doc.close()
                    except Exception as e:
                        st.caption(f"⚠️ Preview could not be generated: {str(e)}")
                else:
                    st.caption("💡 Install PyMuPDF (`pip install pymupdf`) to see preview")

                # ─── Enhanced completion animation ────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                animation_html = """
                <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;'>
                  <style>
                    .unlock-container {
                      width:140px;height:140px;display:flex;align-items:center;justify-content:center;
                      margin:20px auto;
                      perspective: 1000px;
                    }
                    
                    .lock-body {
                      width:80px;height:65px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      border-radius:8px;position:relative;
                      box-shadow:0 8px 24px rgba(102, 126, 234, 0.4);
                      animation: float 3s ease-in-out infinite;
                    }
                    
                    .shackle {
                      width:60px;height:60px;border:6px solid #667eea;border-bottom:0;border-radius:40px;
                      position:absolute;top:-50px;left:10px;transform-origin:center;
                      transform: rotate(0deg);
                      transition: transform 1s cubic-bezier(.2,.8,.2,1);
                      box-shadow:0 4px 12px rgba(102, 126, 234, 0.3);
                    }
                    
                    .shackle.open {
                      transform: rotate(-50deg) translate(-8px,-8px);
                      animation: unlock-spin 0.8s ease-out;
                    }
                    
                    .confetti {
                      position:relative;margin-top:20px;width:240px;height:50px;
                      display:flex;justify-content:center;
                    }
                    
                    .dot {
                      width:10px;height:10px;border-radius:50%;position:absolute;
                      opacity:0;animation:pop 1.2s ease forwards
                    }
                    
                    .dot:nth-child(1){left:20px;background:#ef4444;animation-delay:.2s}
                    .dot:nth-child(2){left:50px;background:#f59e0b;animation-delay:.25s}
                    .dot:nth-child(3){left:80px;background:#eab308;animation-delay:.3s}
                    .dot:nth-child(4){left:110px;background:#10b981;animation-delay:.35s}
                    .dot:nth-child(5){left:140px;background:#3b82f6;animation-delay:.4s}
                    .dot:nth-child(6){left:170px;background:#8b5cf6;animation-delay:.45s}
                    
                    @keyframes unlock-spin {
                      0% { transform: rotate(0deg) scale(0.8); opacity: 0; }
                      50% { opacity: 1; }
                      100% { transform: rotate(-50deg) translate(-8px,-8px) scale(1); }
                    }
                    
                    @keyframes pop {
                      0% { transform:translateY(0) scale(0.1); opacity:0; }
                      50% { opacity:1 }
                      100% { transform:translateY(-40px) scale(1); opacity:0; }
                    }
                    
                    @keyframes float {
                      0%, 100% { transform: translateY(0px); }
                      50% { transform: translateY(-8px); }
                    }
                    
                    .completion-text {
                      font-size: 18px;
                      font-weight: bold;
                      background: linear-gradient(90deg, #667eea, #764ba2, #0ea5a4);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      background-clip: text;
                      margin-top: 20px;
                      animation: slide-in 0.8s ease-out 0.5s both;
                    }
                    
                    @keyframes slide-in {
                      from { opacity: 0; transform: translateY(10px); }
                      to { opacity: 1; transform: translateY(0); }
                    }
                    
                    .sparkle {
                      position: absolute;
                      font-size: 24px;
                      animation: twinkle 1s ease-in-out infinite;
                    }
                    
                    @keyframes twinkle {
                      0%, 100% { opacity: 0.3; }
                      50% { opacity: 1; }
                    }
                    
                    .sparkle:nth-child(1) { top: 10px; left: 20px; animation-delay: 0s; }
                    .sparkle:nth-child(2) { top: 15px; right: 20px; animation-delay: 0.3s; }
                    .sparkle:nth-child(3) { bottom: 20px; left: 15px; animation-delay: 0.6s; }
                    .sparkle:nth-child(4) { bottom: 25px; right: 15px; animation-delay: 0.9s; }
                  </style>
                  
                  <div class='unlock-container'>
                    <div class='sparkle'>✨</div>
                    <div class='lock-body'>
                      <div class='shackle open'></div>
                    </div>
                    <div class='sparkle'>✨</div>
                    <div class='sparkle'>✨</div>
                    <div class='sparkle'>✨</div>
                  </div>
                  
                  <div class='confetti'>
                    <div class='dot'></div>
                    <div class='dot'></div>
                    <div class='dot'></div>
                    <div class='dot'></div>
                    <div class='dot'></div>
                    <div class='dot'></div>
                  </div>
                  
                  <div class='completion-text'>✨ Your PDF is Ready! ✨</div>
                </div>
                
                <script>
                  const sh = document.querySelector('.shackle');
                  setTimeout(() => { sh.classList.add('open'); }, 300);
                </script>
                """

                components.html(animation_html, height=280)

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

# ──── FOOTER ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔐 **Privacy:** No data is stored on servers")
with col2:
    st.caption("⚖️ **Legal:** Use responsibly with owned files")
with col3:
    st.caption(f"📅 **Version:** {time.strftime('%Y-%m')}")

st.caption("Built with ❤️ using Streamlit • PyPDF2 • PyMuPDF")
