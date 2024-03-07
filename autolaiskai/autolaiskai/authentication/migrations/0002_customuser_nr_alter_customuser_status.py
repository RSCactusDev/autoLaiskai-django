# Generated by Django 4.1 on 2024-02-27 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='nr',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='status',
            field=models.CharField(choices=[('regular', 'regular'), ('trial', 'trial'), ('premium', 'premium')], default='regular', max_length=20),
        ),
    ]