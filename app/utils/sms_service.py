from twilio.rest import Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Twilio client
try:
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
except Exception as e:
    logger.warning(f"Twilio client initialization failed: {e}")
    twilio_client = None

def send_sms(to: str, message: str):
    """
    Send SMS using Twilio
    In production, this would integrate with actual SMS service
    """
    try:
        # For demo purposes, we'll simulate SMS sending
        # In real implementation, you would use:
        # if twilio_client:
        #     message = twilio_client.messages.create(
        #         body=message,
        #         from_=settings.TWILIO_PHONE_NUMBER,
        #         to=to
        #     )
        #     return message.sid
        
        logger.info(f"SMS sent to {to}: {message}")
        return f"simulated_sms_{to}"
        
    except Exception as e:
        logger.error(f"SMS sending failed: {e}")
        raise e

def send_otp(phone_number: str, otp: str):
    """
    Send OTP for verification
    """
    message = f"Your NEXA verification code is: {otp}. Valid for 10 minutes."
    return send_sms(phone_number, message)