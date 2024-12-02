from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template


def send_email_with_content(subject, content, reciever):
    sender = settings.EMAIL_HOST_USER
    send_mail(
        subject=subject,
        message='',
        from_email=sender,
        recipient_list=[reciever],
        fail_silently=False,
        html_message=content,
    )


def send_profile_update_mail(email_data):
    html_template = get_template('emails/profile_completion_for_project.html')
    html_alternative = html_template.render(email_data)
    subject = "Account Update Required"
    reciever = email_data['email']

    send_email_with_content(subject, html_alternative, reciever)
