import base64
import json
from django.conf import settings
import qrcode
import io
import bcrypt
from django.contrib import messages
from django.core.mail import EmailMessage
from .models import Participant
from random import randint
import requests
import jwt
from celery import shared_task

public_webhook_url = settings.WEBHOOK_URLS["public"]
organizer_webhook_url = settings.WEBHOOK_URLS["organizer"]

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@shared_task
def send_checkin_qr_email(participant_list_dict):
     for participant_data in participant_list_dict:
        participant = Participant.objects.get(id=int(participant_data['id']))
        passcode = str(random_with_N_digits(6))
        qr_data = {
            "id": participant.id,
            "passcode": passcode
        }
        
        qr_json_payload = json.dumps(qr_data)
        qr_json_payload_b64 = base64.b64encode(qr_json_payload.encode())
        qr = qrcode.QRCode(version=None, box_size=10, border=4)
        qr.add_data(qr_json_payload_b64)
        qr.make(fit=True)
        qrimg = qr.make_image(fill_color="black", back_color="white")
        qrimg_byte_arr = io.BytesIO()
        qrimg.save(qrimg_byte_arr, format='PNG')
        qrimg_byte_arr = qrimg_byte_arr.getvalue()
        
        participant.passCode = bcrypt.hashpw(passcode.encode(), bcrypt.gensalt())
        participant.save()
        # Replace the placeholders with the actual email content
        subject = f"{settings.EMAIL_EVENT_NAME} 체크인 QR 코드 및 인증코드 Your Check-in QR Code and Passcode"
        message = f"""
        {participant.name}님 안녕하세요,
        {settings.EMAIL_EVENT_NAME}에 참가 등록 해 주셔서 감사합니다.
        행사장에서 체크인과 명찰 발급에 사용할 수 있는 QR코드와 인증코드를 발급하여 첨부 해 드렸습니다.
        QR 코드를 이용하는 경우, 첨부된 QR 코드 이미지를 행사장에서 스캔 하시고,
        인증 코드를 이용하는 경우, 아래 6자리 코드를 입력 하시면 됩니다.

        인증코드: {passcode}

        감사합니다.
        {settings.EMAIL_SENDER_NAME} 드림.

        Hello {participant.name},
        Thank you for registering to {settings.EMAIL_EVENT_NAME}.
        We've attached and QR Code and passcode that you can use to Check-in and print your badge.
        If you're using the QR code, please scan the QR code at the venue,
        or if you're using passcode, please enter the following 6-digit code on kiosk.

        Passcode: {passcode}

        Best regards,
        {settings.EMAIL_SENDER_NAME}
        """
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_SENDER,
            [participant.email],
            [],
            reply_to=[settings.EMAIL_REPLY_TO],
            headers={},
        )
        email.attach("checkin_qr.png", qrimg_byte_arr, "image/png")
        email.send()

@shared_task
def send_checkin_confirm(participant_id):
    participant = Participant.objects.get(id=int(participant_id))
    subject = f"{settings.EMAIL_EVENT_NAME} 체크인 완료"
    message = f"""
    {participant.name}님 안녕하세요,
    {settings.EMAIL_EVENT_NAME} 체크인이 완료 되었습니다.
    {settings.EMAIL_SENDER_NAME} 드림.
    Hello {participant.name},
    You have successfully checked in for {settings.EMAIL_EVENT_NAME}.
    Hope you enjoy the event!
    Best regards,
    {settings.EMAIL_SENDER_NAME}
    """
    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_SENDER,
        [participant.email],
        [],
        reply_to=[settings.EMAIL_REPLY_TO],
        headers={},
    )
    email.send()
    webhook_payload = {
        "text": f"{participant.name}님이 행사장에 도착했습니다!"
    }
    requests.post(public_webhook_url, json=webhook_payload)
    requests.post(organizer_webhook_url, json=webhook_payload)