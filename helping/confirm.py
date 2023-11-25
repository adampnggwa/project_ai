import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configs import config

SERVER = 'smtp.gmail.com'
PORT = 587
MY_EMAIL = config.my_email
MY_PASSWORD = config.my_password

def send_confirm(email: str, token: str, exp: str):
    msg = MIMEMultipart()

    subject = "Confirmation Token for Ai Text to Image Application"
    sender_name = "Ai Text to Image Team"
    sender_email = "no-reply@aiimage.com"  

    message_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background-color: #f4f4f4; padding: 20px;">
            <h2 style="color: #333;">{subject}</h2>
            <p>Dear User,</p>
            <p>Thank you for choosing Ai Text to Image. Here is your confirmation token:</p>
            <p style="font-size: 18px; background-color: #ddd; padding: 10px;">{token}</p>
            <p>Please use this token before it expires, to access our features and verify your identity in the Ai Text to Image application.</p>
            <p>Token Expiration: {exp}, verification token will expire in 5 minutes, if your verification token has expired you have to sign up again</p>
            <p>If you want to continue verification, please click <a href="http://127.0.0.1:8000/docs#/auth-local/verify_registration_auth_local_verify_registration_post">here</a> to continue. Thank you for your support!</p>
            <p style="margin-top: 20px;">Best regards,</p>
            <p>{sender_name}</p>
        </div>
    </body>
    </html>
    """

    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'html'))
    server = smtplib.SMTP(SERVER, PORT)
    try:
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.sendmail(sender_email, email, msg.as_string())
        print('Email successfully sent!')
    except Exception as e:
        print('An error occurred:', str(e))
    finally:
        server.quit()