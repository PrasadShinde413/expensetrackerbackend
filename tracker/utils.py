import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generates a random 6-digit string OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Sends a real email to the user using SMTP settings from settings.py."""
    subject = "Your Verification OTP - Expense Tracker"
    message = f"""
    Hello,
    
    Welcome to Expense Tracker! 
    Your verification code is: {otp}
    
    This code is valid for registration only. If you didn't request this, ignore this email.
    
    Regards,
    Team Prasad and Sneha
    """
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"CRITICAL ERROR sending email: {str(e)}")
        return False