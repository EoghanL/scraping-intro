from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context, loader

from proj_utils.redis_client import RedisAsyncClient


def send_email(recipients, subject, body, async=True, **kwargs):
    from_email = kwargs.get('from_email', settings.DEFAULT_FROM_EMAIL)
    cc = kwargs.get('cc', [])

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=recipients,
        cc=cc
    )

    if not async:
        msg.send()
    else:
        redis_client = RedisAsyncClient()
        redis_client.enqueue_default(msg.send)


def send_template_email(recipients, subject, template_name, context, async=True, **kwargs):
    template = loader.get_template(template_name)
    ctx = Context(context)

    body = template.render(ctx)
    send_email(recipients, subject, body, async, **kwargs)
