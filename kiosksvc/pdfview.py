from weasyprint import HTML
from django.template.loader import render_to_string
from kiosksvc.models import CheckInLog, Participant
from django import forms
from django.shortcuts import render
import io
from django.conf import settings
from django.core.mail import EmailMessage
import base64 
from django.utils import timezone
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class EmailForm(forms.Form):
    email = forms.EmailField(label="email", max_length=100)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(
        attrs={
            'data-size': 'compact',
        }
    ))


def attendee_cert_request(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            email_addr = form.cleaned_data["email"]
            participant = Participant.objects.filter(email=email_addr).first()
            if participant is None:
                return render(request, "kiosksvc/reqcert.html", {"form": EmailForm(), "request_done": True})
            checkin = CheckInLog.objects.filter(participant=participant).first()
            if checkin is None:
                return render(request, "kiosksvc/reqcert.html", {"form": EmailForm(), "request_done": True})
            certstamp = open(settings.EMAIL_CERTSTAMP_PATH, 'rb').read()
            # buffer = io.BytesIO(target=certstamp)
            # buffer to base64
            certstamp_b64 = base64.b64encode(certstamp).decode()
            certstamp_datauri = f"data:image/png;base64,{certstamp_b64}"
            print(certstamp_datauri)
            html = render_to_string(
                "kiosksvc/attndcert.html",
                {
                    "name": participant.name,
                    "affiliation": participant.affilation,
                    "role": participant.role,
                    "checkedInAt": checkin.checkedInAt,
                    "stampImage": certstamp_datauri,
                    "year": timezone.now().year,
                    "month": timezone.now().month,
                    "day": timezone.now().day,
                },
            )
            buffer = io.BytesIO()
            HTML(string=html).write_pdf(target=buffer)

            subject = f"{settings.EMAIL_EVENT_NAME} 참가확인증 Certificate of attendance"
            message = f"""
            {participant.name}님 안녕하세요,

            지난 {settings.EMAIL_EVENT_NAME}에 참가 해 주셔서 감사합니다.
            요청하신 참가 확인증을 첨부 하였으니 확인 해 보시기 바랍니다.

            감사합니다.
            {settings.EMAIL_SENDER_NAME} 드림.

            Hello {participant.name},

            Thank you for joining {settings.EMAIL_EVENT_NAME}.
            We've attached the certificate of attendance you requested.

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
            email.attach("certificate.pdf", buffer.getvalue(), "application/pdf")
            try:
                email.send()
            except Exception as e:
                print(e)
        return render(request, "kiosksvc/reqcert.html", {"form": EmailForm(), "request_done": True})
    else:
        form = EmailForm()
        return render(request, "kiosksvc/reqcert.html", {"form": form})
