from django.db import models


class Address(models.Model):
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=30)
    city = models.CharField(max_length=120)
    state_region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, default="Switzerland")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["postal_code"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.line1}, {self.postal_code} {self.city}"
