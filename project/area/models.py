from django.db import models
from django.db.models import F


class Area(models.Model):
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.city}, {self.state}"


class City(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = (("name", "state"),)

    def __str__(self):
        return f"{self.name}, {self.state}"


class UserCity(models.Model):
    user = models.ForeignKey('core_auth.User', on_delete=models.CASCADE)
    city = models.ForeignKey('area.City', on_delete=models.CASCADE)
    score = models.IntegerField(default=1, blank=True)

    def __str__(self):
        return self.city.__str__()

    def incr_score(self):
        self.score = F('score') + 1
        self.save()
