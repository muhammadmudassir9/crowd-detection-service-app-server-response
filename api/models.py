from django.db import models

# Create your models here.


class User(models.Model):
    image = models.ImageField(upload_to="media/")

    crowd_count = models.IntegerField(default=None)

    time = models.DateTimeField()

    alert = models.CharField(max_length=255)

    def __str__(self):
        return self.image.url
