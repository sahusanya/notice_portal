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


class NoticeLog(models.Model):
    customer_name = models.CharField(max_length=255)
    loan_account = models.CharField(max_length=100, null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)  # Link to Template used
    email = models.EmailField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Link to Company
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure')
        ]
    )
    reason = models.TextField(null=True, blank=True)  # Store failure reason if any
    user_friendly_reason = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Time of generation attempt
    pdf_file = models.FileField(upload_to='notices/', blank=True, null=True)

    def __str__(self):
        return f"{self.customer_name} | {self.status} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
