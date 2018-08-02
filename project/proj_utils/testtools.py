from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import RequestFactory


class SimpleFractalTestCaseMixin(object):

    def assertSingleMessage(self, response, msg, level):
        self.assertEqual(1, len(response.context['messages']))
        for message in response.context['messages']:
            self.assertEqual(msg, message.message)
            self.assertEqual(level, message.level)

    def assertEmail(self, email, recipients, subject='', body='', from_email=''):
        email_recipients = sorted(email.recipients())
        self.assertEqual(email_recipients, sorted(recipients))
        self.assertEqual(from_email or settings.DEFAULT_FROM_EMAIL, email.from_email)
        if subject:
            self.assertEqual(subject, email.subject)
        if body:
            self.assertEqual(body, email.body)

    def assertNotRecipient(self, email, recipient):
        email_recipients = sorted(email.recipients())
        self.assertNotIn(recipient, email_recipients)


class ModelAdminTestCaseMixin(SimpleFractalTestCaseMixin):

    def get_request(self, user=None):
        request = RequestFactory().get('/')
        if user:
            request.user = user
        return request

    def perform_action(self, action, queryset, **kwargs):
        self.assertTrue(queryset, msg="Can't perform action on unexisting queryset")

        model_meta = queryset.model._meta
        url = reverse(
            'admin:{}_{}_changelist'.format(model_meta.app_label, model_meta.object_name.lower())
        )

        data = {
            '_selected_action': [obj.pk for obj in queryset],
            'index': 0,
            'action': action,
        }
        data.update(**kwargs)
        return self.client.post(url, data, follow=True)
