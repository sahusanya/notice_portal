from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Template(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='templates')
    template_type = models.CharField(max_length=50)   # E.g. 'legal_notice'
    subject = models.CharField(max_length=200)
    body = models.TextField()
    email_body = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.template_type}"
