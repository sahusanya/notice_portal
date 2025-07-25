from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()

    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    email_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
