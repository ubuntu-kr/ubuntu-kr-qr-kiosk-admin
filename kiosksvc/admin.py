from django.contrib import admin
from django.contrib import messages
from django.core.mail import send_mail


# Register your models here.
class ParticipantAdmin(admin.ModelAdmin):
    @admin.action(description="체크인 QR 이메일 발송", permissions=["change"])
    def send_checkin_qr_email(self, request, queryset):
        for participant in queryset:
            # Replace the placeholders with the actual email content
            subject = 'UbuCon Korea 2023 체크인 QR 코드'
            message = 'Message of the email'
            from_email = ""
            to_email = [participant.email]  # Assuming the email field is called 'email'

            try:
                send_mail(subject, message, from_email, to_email)
            except Exception as e:
                messages.error(request, f"Failed to send email to {object.email}: {e}")
            else:
                messages.success(request, f"Email sent successfully to {object.email}")

