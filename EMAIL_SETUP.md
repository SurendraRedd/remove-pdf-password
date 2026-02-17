# 📧 Email Setup Guide

This guide will help you set up email notifications for the PDF Unlocker contact form.

## Quick Setup

### Option 1: Gmail (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character password

3. **Create `.env` file in your project root:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   RECIPIENT_EMAIL=admin@example.com
   ```

4. **Restart Streamlit**
   ```bash
   streamlit run app.py
   ```

### Option 2: Outlook / Microsoft 365

1. **Get Your Email Settings**
   - SMTP Server: `smtp-mail.outlook.com`
   - SMTP Port: `587`
   - Email: Your Outlook email address
   - Password: Your Outlook password

2. **Create `.env` file:**
   ```
   SMTP_SERVER=smtp-mail.outlook.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@outlook.com
   SENDER_PASSWORD=your-outlook-password
   RECIPIENT_EMAIL=admin@example.com
   ```

3. **Restart Streamlit**

### Option 3: Custom SMTP Server

1. **Get your SMTP details from your email provider**
2. **Create `.env` file with your settings:**
   ```
   SMTP_SERVER=your-smtp-server.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@yourdomain.com
   SENDER_PASSWORD=your-password
   RECIPIENT_EMAIL=admin@yourdomain.com
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (usually 587) | `587` |
| `SENDER_EMAIL` | Email to send from | `noreply@example.com` |
| `SENDER_PASSWORD` | Email password or app password | `your-app-password` |
| `RECIPIENT_EMAIL` | Where to send admin notifications | `admin@example.com` |

## Setting Environment Variables

### Local Development

1. **Create `.env` file in project root:**
   ```bash
   touch .env
   ```

2. **Add your credentials:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   RECIPIENT_EMAIL=admin@example.com
   ```

3. **Load with python-dotenv (optional):**
   ```bash
   pip install python-dotenv
   ```

4. **In your app (add to top of app.py):**
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Streamlit Cloud Deployment

1. Go to your Streamlit app settings
2. Click "Secrets" or "Advanced Settings"
3. Add environment variables:
   ```
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = "587"
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   RECIPIENT_EMAIL = "admin@example.com"
   ```

### Docker / Server Deployment

Export variables before running:
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password
export RECIPIENT_EMAIL=admin@example.com

streamlit run app.py
```

Or in `docker-compose.yml`:
```yaml
environment:
  SMTP_SERVER: smtp.gmail.com
  SMTP_PORT: "587"
  SENDER_EMAIL: your-email@gmail.com
  SENDER_PASSWORD: your-app-password
  RECIPIENT_EMAIL: admin@example.com
```

## How It Works

When a user submits the contact form:

1. ✅ Message is saved to `contact_submissions.json` (local backup)
2. ✅ Confirmation email is sent to the user
3. ✅ Notification email is sent to `RECIPIENT_EMAIL`

### Confirmation Email (to user)
- Thanks them for contacting
- Repeats their message back
- Assures them of response

### Notification Email (to admin)
- Shows all submission details
- Includes timestamp
- Ready for response

## Troubleshooting

### "Email sending error: SMTP Authentication failed"
- ❌ Wrong password
- ✅ Solution: Double-check `SENDER_PASSWORD` (Gmail: use app password, not account password)

### "Email sending error: Connection refused"
- ❌ Wrong SMTP server or port
- ✅ Solution: Verify `SMTP_SERVER` and `SMTP_PORT`

### Emails not being received
- ✅ Check spam folder
- ✅ Verify recipient email is correct
- ✅ Check if 2FA is enabled for Gmail
- ✅ Ensure app password (not regular password) is used

### "No module named 'dotenv'"
- Optional: Install with `pip install python-dotenv`
- Or just use system environment variables

### Messages saved but no email sent
- App continues to work even if email fails
- All messages are saved to `contact_submissions.json`
- Check logs for email errors

## Security Best Practices

✅ **Always use `.env` file** (never hardcode passwords)  
✅ **Use app-specific passwords** for Gmail instead of your main password  
✅ **Never commit `.env` to git**  
✅ **Add `.env` to `.gitignore`:**
   ```
   echo ".env" >> .gitignore
   ```

✅ **For production, use secrets management:**
- Streamlit Cloud: Use Secrets
- Docker: Use environment variables
- AWS: Use Secrets Manager
- Azure: Use Key Vault

## Testing Email Configuration

Run this Python script to test your setup:

```python
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load credentials
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

try:
    print("🔍 Testing email configuration...")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Port: {SMTP_PORT}")
    print(f"Sender Email: {SENDER_EMAIL}")
    print(f"Recipient Email: {RECIPIENT_EMAIL}")
    
    # Create message
    message = MIMEMultipart()
    message["Subject"] = "Test Email - PDF Unlocker"
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL
    
    body = MIMEText("This is a test email from PDF Unlocker.", "plain")
    message.attach(body)
    
    # Send
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
    
    print("✅ Email test successful! Configuration is working.")
    
except Exception as e:
    print(f"❌ Email test failed: {str(e)}")
    print("Please check your configuration.")
```

## Support

Having issues? Check:
1. Environment variables are set correctly
2. Email password is the app-specific password (for Gmail)
3. 2FA is enabled for Gmail accounts
4. Check spam folder for test emails
5. Verify SMTP server and port are correct for your provider

---

**Once configured, contact form submissions will automatically send emails! 📧**
