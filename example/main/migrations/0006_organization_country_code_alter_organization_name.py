# Generated by Django 4.0.6 on 2022-07-13 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_organization_person_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='country_code',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=250),
        ),
    ]
