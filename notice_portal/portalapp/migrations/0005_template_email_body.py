# Generated by Django 5.2.4 on 2025-07-25 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portalapp', '0004_rename_content_template_body_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='email_body',
            field=models.TextField(blank=True, null=True),
        ),
    ]
