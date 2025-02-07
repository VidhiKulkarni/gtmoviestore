from django.db import models

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    description = models.TextField()
    image = models.URLField()  # Use URLField to store poster URL from OMDb

    def __str__(self):
        return f"{self.id} - {self.name}"

