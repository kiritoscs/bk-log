# Generated by Django 3.2.5 on 2022-07-19 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_search", "0046_logindexset_bcs_project_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="logindexset",
            name="bcs_project_id",
            field=models.CharField(default="", max_length=64, verbose_name="项目ID"),
        ),
    ]
