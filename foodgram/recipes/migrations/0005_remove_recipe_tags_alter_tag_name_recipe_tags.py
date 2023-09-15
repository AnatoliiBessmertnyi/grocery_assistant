# Generated by Django 4.2.5 on 2023-09-15 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_tag_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='tags',
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Название тэга'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
