# Generated by Django 3.2.5 on 2022-08-31 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("log_measure", "0008_auto_20211209_1926"),
    ]

    operations = [
        migrations.CreateModel(
            name="MetricDataHistory",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("metric_id", models.CharField(max_length=256, verbose_name="指标ID")),
                ("metric_data", models.TextField(verbose_name="指标数据")),
                ("updated_at", models.IntegerField(verbose_name="指标时间戳")),
            ],
        ),
    ]