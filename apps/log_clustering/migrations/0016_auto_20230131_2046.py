# Generated by Django 3.2.15 on 2023-01-31 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_clustering", "0015_alter_clusteringconfig_after_treat_flow_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="clusteringconfig",
            name="options",
            field=models.JSONField(blank=True, null=True, verbose_name="额外配置"),
        ),
        migrations.AddField(
            model_name="clusteringconfig",
            name="task_records",
            field=models.JSONField(default=list, verbose_name="任务记录"),
        ),
    ]
