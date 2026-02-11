# app.py
# PDF Password Remover ────────────────────────────────────────────────────────
# A simple Streamlit app to remove known passwords from PDF files

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import time

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
    st.code("pip install streamlit PyPDF2 pymupdf", language="bash")

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
        with st.status("Processing PDF...", expanded=True) as status:
            try:
                # ─── Read file ────────────────────────────────
                pdf_bytes = uploaded_file.getvalue()
                pdf_stream = io.BytesIO(pdf_bytes)

                reader = PdfReader(pdf_stream)

                status.update(label="Checking encryption...", state="running")

                if not reader.is_encrypted:
                    status.update(
                        label="This PDF is not password protected.",
                        state="complete"
                    )
                    st.info("No password was detected. You can download the file as-is.")
                else:
                    status.update(label="Trying to decrypt...", state="running")

                    decrypt_result = reader.decrypt(password)

                    if decrypt_result == 0:
                        status.update(label="Wrong password", state="error")
                        st.error("Decryption failed → incorrect password.")
                        st.stop()

                    status_text = {
                        1: "User password accepted (some restrictions may remain)",
                        2: "Owner/full password accepted → complete unlock"
                    }.get(decrypt_result, "Decrypted (unknown result code)")

                    status.update(label=status_text, state="running")

                # ─── Create clean PDF ─────────────────────────
                status.update(label="Creating unprotected version...", state="running")

                writer = PdfWriter()

                for i, page in enumerate(reader.pages, 1):
                    writer.add_page(page)

                # Try to keep original metadata
                try:
                    writer.add_metadata(reader.metadata or {})
                except:
                    pass

                # Write to memory
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)

                status.update(label="Done!", state="complete")

                # ─── Filename logic ────────────────────────────
                base, ext = os.path.splitext(uploaded_file.name)
                new_name = f"{base} - unlocked{ext}"

                # ─── Download button ───────────────────────────
                st.download_button(
                    label=f"⬇️ Download unlocked PDF ({file_size_mb:.1f} MB)",
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
                            pix = doc[0].get_pixmap(dpi=90)
                            st.image(pix.tobytes("png"), use_column_width=True)
                        doc.close()
                    except Exception as e:
                        st.caption("Preview could not be generated.")
                else:
                    st.caption("Install PyMuPDF (`pip install pymupdf`) to see preview")

            except Exception as e:
                status.update(label="Error occurred", state="error")
                st.error("Could not process this PDF file.")
                with st.expander("Error details"):
                    st.exception(e)

else:
    st.info("Upload a password-protected PDF file to start.", icon="📄")

st.markdown("---")
st.caption(f"PDF Unlocker • {time.strftime('%Y-%m')}")