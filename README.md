# 🔓 PDF Unlocker

A lightweight Streamlit web application to safely remove password protection from PDF files (when you know the password).

## ✨ Features

- 🔐 **Secure Decryption**: Remove user passwords from password-protected PDFs
- 👁️ **First-Page Preview**: View a preview of the first page (requires PyMuPDF)
- 📊 **Real-time Progress**: Monitor decryption progress with visual feedback
- 📈 **File Analytics**: See file size, page count, and processing time
- 🎨 **Beautiful UI**: Clean, intuitive interface built with Streamlit
- 📚 **Interactive Guide**: Step-by-step "How to Use" section in expandable format
- 📬 **Contact Form**: Easy way for users to provide feedback and report issues
- ⚡ **Optimized Performance**: Handles files up to 150 MB efficiently

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/SurendraRedd/remove-pdf-password.git
cd remove-pdf-password
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Requirements

- Python 3.8+
- Streamlit >= 1.38.0
- PyPDF2 >= 3.0.1
- pymupdf >= 1.24.10 (optional, for PDF preview)
- pycryptodome >= 3.17.0 (for AES encryption support)

## 🎯 How to Use

### Step-by-Step

1. **Upload Your PDF** - Select your password-protected PDF file
2. **Enter Password** - Type the correct password (case-sensitive)
3. **Click Remove Password** - Watch the progress indicator
4. **Download** - Get your unlocked PDF with a clean filename
5. **Preview** - Optionally view the first page preview

### Security & Privacy

✅ **No data storage** - Files are processed locally only  
✅ **No server upload** - Everything happens in your browser session  
✅ **Auto-deletion** - Files are cleared after download or page refresh  
✅ **HTTPS ready** - Use HTTPS connections for maximum security  

## ⚠️ Important Notes

- ✓ Works with user passwords
- ✗ Does NOT remove owner/restriction passwords
- ✗ May timeout on files larger than 150 MB
- ✓ Ensure you own the file or have permission to decrypt it

## 💬 Contact & Feedback

We'd love to hear from you! Use the **"Get in Touch"** contact form at the bottom of the app to:
- Report bugs
- Request features
- Provide general feedback
- Get technical support

All submissions are saved and will be reviewed.

## 🛠️ Project Structure

```
remove-pdf-password/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Code Features

### Utility Functions

- `validate_email()` - Client-side email validation
- `save_contact_submission()` - Saves contact form data to JSON
- `format_file_size()` - Converts bytes to MB with precision
- `get_generated_filename()` - Generates clean output filenames

### Configuration

All settings are centralized as constants:
```python
MAX_FILE_SIZE_MB = 150      # Maximum file size limit
WARN_FILE_SIZE_MB = 80      # Warning threshold
DEFAULT_DPI = 120           # Preview DPI
PREVIEW_WIDTH = 700         # Preview width in pixels
```

## 📝 Contact Form Features

- ✓ Name and email validation
- ✓ Subject selection (Bug Report, Feature Request, etc.)
- ✓ Message text area with character limit
- ✓ JSON-based submission storage
- ✓ Timestamp tracking
- ✓ Success/error feedback

## 🐛 Troubleshooting

### "Incorrect password"
- Verify the password is correct (case-sensitive)
- Check for extra spaces
- Ensure the file is actually password-protected

### "AES encryption requires PyCryptodome"
```bash
pip install pycryptodome
```

### Processing timeout
- File may be too large
- Try splitting the PDF into smaller parts
- Check system resources

### Preview not showing
- Install PyMuPDF: `pip install pymupdf`
- Restart the app

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Contributing

Contributions are welcome! Please feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📧 Support

For questions or support, use the contact form in the app or open an issue on GitHub.

---

**Built with ❤️ using Streamlit • PyPDF2 • PyMuPDF**
