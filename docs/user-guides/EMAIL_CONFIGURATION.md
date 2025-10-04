# Email Configuration Guide

## Required Environment Variables

Add these environment variables to your `.env` file for email functionality:

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=noreply@billionsbounty.com

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
```

## Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password as `SMTP_PASSWORD`

## Alternative Email Providers

### SendGrid
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

### AWS SES
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your_ses_username
SMTP_PASSWORD=your_ses_password
```

## Email Templates

The system includes two email templates:

1. **Email Verification**: Sent when users sign up
2. **Password Reset**: Sent when users request password reset

Both templates are HTML-formatted with:
- Responsive design
- Branded styling
- Clear call-to-action buttons
- Security information
- Expiration notices

## Testing

For development, you can test without SMTP by checking the response for the `token` field, which contains the verification token for testing purposes.
