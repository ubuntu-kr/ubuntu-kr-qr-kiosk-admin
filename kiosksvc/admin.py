from django.contrib import admin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from josepy.jwk import RSAKey
from josepy.jws import JWS
import uuid
import qrcode


# Register your models here.
class ParticipantAdmin(admin.ModelAdmin):
    @admin.action(description="체크인 QR 이메일 발송", permissions=["change"])
    def send_checkin_qr_email(self, request, queryset):
        with open(settings.CHECKIN_QR_CONFIG["private_key_path"], 'rb') as f:
            private_key = RSAKey.from_pem(f.read())
        jwk = private_key.key

        for participant in queryset:
            jwt_payload = {
                "sub": participant.id,
                "tid": str(uuid.uuid1()),
                "nametagName": participant.name,
                "nametagAffiliation": participant.affilation,
                "nametagRole": participant.role,
                "nametagUrl": participant.qrUrl
            }
            jws = JWS.sign(jwt_payload, jwk)
            jwt = jws.serialize(compact=True)
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(jwt)
            qr.make(fit=True)
            qrimg = qr.make_image(fill_color="black", back_color="white")

            # Replace the placeholders with the actual email content
            subject = f'{settings.EMAIL_EVENT_NAME} 체크인 QR 코드'
            message = f"""
            {participant.name}님 안녕하세요,

            {settings.EMAIL_EVENT_NAME}에 참가 등록 해 주셔서 감사합니다.
            행사장에서 체크인과 명찰 발급에 사용할 수 있는 QR코드를 발급하여 첨부 해 드렸습니다.
            첨부된 QR코드 이미지를 열어 행사장에서 이용하시기 바랍니다.

            감사합니다.
            {settings.EMAIL_SENDER_NAME} 드림.
            """
            from_email = settings.EMAIL_SENDER
            to_email = [participant.email]  # Assuming the email field is called 'email'

            try:
                send_mail(subject, message, from_email, to_email)
            except Exception as e:
                messages.error(request, f"Failed to send email to {object.email}: {e}")
            else:
                messages.success(request, f"Email sent successfully to {object.email}")

