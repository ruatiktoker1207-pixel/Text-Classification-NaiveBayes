# Email Configuration for OTP Sending
# ====================================
# You need to set up Gmail to send OTP emails

# IMPORTANT: Follow these steps to get your app-specific password:
# 1. Enable 2-Step Verification on your Google Account
# 2. Go to https://myaccount.google.com/apppasswords
# 3. Select "Mail" and "Windows Computer" (or your device)
# 4. Google will generate a 16-character password
# 5. Copy that password and paste it below in EMAIL_PASSWORD

# OR use a different email provider by updating SMTP_SERVER and SMTP_PORT

EMAIL_ADDRESS = "your_email@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"  # Your app-specific password (16 characters from step 4 above)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_EXPIRY_MINUTES = 10
