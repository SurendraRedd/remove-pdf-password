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

st.set_page_config(
    page_title="PDF Unlocker",
    page_icon="🔓",
    layout="centered",
    initial_sidebar_state="expanded"
)

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

# ──── MAIN AREA ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your password-protected PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Only single PDF files are supported at the moment"
)

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / 1_048_576  # more accurate than 1024*1024

    # Size feedback
    if file_size_mb > 150:
        st.error(f"File is very large ({file_size_mb:.1f} MB) → high risk of timeout or memory error.")
        st.stop()
    elif file_size_mb > 80:
        st.warning(f"Large file detected ({file_size_mb:.1f} MB). Processing may be slow.")
    else:
        st.success(f"File loaded: {file_size_mb:.1f} MB", icon="✅")

    st.markdown(f"**Filename:** {uploaded_file.name}")

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
                base, ext = os.path.splitext(uploaded_file.name)
                new_name = f"{base} - unlocked{ext}"

                orig_mb = uploaded_file.size / 1_048_576
                out_mb = len(output.getvalue()) / 1_048_576
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
                            pix = doc[0].get_pixmap(dpi=120)
                            st.image(pix.tobytes("png"), width=700)
                        doc.close()
                    except Exception:
                        st.caption("Preview could not be generated.")
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
st.caption(f"PDF Unlocker • {time.strftime('%Y-%m')}")
