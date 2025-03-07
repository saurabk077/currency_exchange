from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.IntegerField(default=1)  # Lower number means higher priority
    active = models.BooleanField(default=True)  # Allows dynamic activation/deactivation

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name