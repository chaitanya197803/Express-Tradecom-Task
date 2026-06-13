from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=100)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.role})"
