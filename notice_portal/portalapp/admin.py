from django.contrib import admin

# Register your models here.
from .models import Company, Template

admin.site.register(Company)
admin.site.register(Template)
