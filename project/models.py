import hashlib

from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField


class Merchant(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    fuzzy_match_store_ids = models.BooleanField(default=False)
    fuzzy_match_fallback = models.BooleanField(default=False)


class StoreLocation(models.Model):
    merchant = models.ForeignKey('engine.Merchant', on_delete=models.CASCADE)
    store_id = models.CharField(max_length=50)
    normalized_store_id = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=20)

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
