import django_rq

from django.conf import settings


class RedisAsyncClient(object):

    @property
    def default_queue(self):
        return django_rq.get_queue('default')

    def enqueue_default(self, callable, *args, **kwargs):
        if settings.TESTING:
            callable(*args, **kwargs)
        else:
            self.default_queue.enqueue(callable, args=args, kwargs=kwargs)


class NullableClient(object):
    """
    https://robots.thoughtbot.com/rails-refactoring-example-introduce-null-object
    """

    def enqueue_default(self, callable, *args, **kwargs):
        return callable(*args, **kwargs)
