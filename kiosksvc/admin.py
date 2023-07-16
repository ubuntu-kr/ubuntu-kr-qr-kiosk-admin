from django.contrib import admin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from cryptography.hazmat.primitives import serialization
import jwt
import uuid
import qrcode
import io
import gzip
import base64
from .models import Participant



# Register your models here.
class ParticipantAdmin(admin.ModelAdmin):
    actions = ['send_checkin_qr_email', ]
    @admin.action(description="체크인 QR 이메일 발송", permissions=["change"])
    def send_checkin_qr_email(self, request, queryset):
        private_key = open(settings.CHECKIN_QR_CONFIG["private_key_path"], 'r').read()
        key = serialization.load_pem_private_key(private_key.encode(), password=None)

        for participant in queryset:
            jwt_payload = {
                "sub": participant.id,
                "tid": str(uuid.uuid1()),
                "nametagName": participant.name,
                "nametagAffiliation": participant.affilation,
                "nametagRole": participant.role,
                "nametagUrl": participant.qrUrl,
            }
            
            new_token = jwt.encode(
                payload=jwt_payload,
                key=key,
                algorithm='ES256'
            )
            # new_token_gzip = gzip.compress(bytes(new_token, 'utf-8'))
            # base64_token = str(base64.b64encode(new_token_gzip))
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(new_token)
            qr.make(fit=True)
            qrimg = qr.make_image(fill_color="black", back_color="white")
            qrimg_byte_arr = io.BytesIO()
            qrimg.save(qrimg_byte_arr, format='PNG')
            qrimg_byte_arr = qrimg_byte_arr.getvalue()

            # Replace the placeholders with the actual email content
            subject = f"{settings.EMAIL_EVENT_NAME} 체크인 QR 코드"
            message = f"""
            {participant.name}님 안녕하세요,

            {settings.EMAIL_EVENT_NAME}에 참가 등록 해 주셔서 감사합니다.
            행사장에서 체크인과 명찰 발급에 사용할 수 있는 QR코드를 발급하여 첨부 해 드렸습니다.
            첨부된 QR코드 이미지를 열어 행사장에서 이용하시기 바랍니다.

            감사합니다.
            {settings.EMAIL_SENDER_NAME} 드림.
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
            try:
                email.send()
            except Exception as e:
                messages.error(request, f"{participant.email}(으)로 이메일을 발송하지 못했습니다.: {e}")
            else:
                messages.success(request, f"체크인 QR 코드가 담긴 이메일을 {participant.email}(으)로 잘 발송했습니다.")
admin.site.register(Participant, ParticipantAdmin)
