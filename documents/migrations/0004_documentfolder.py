from django.db import migrations, models


def seed_default_folders(apps, schema_editor):
    DocumentFolder = apps.get_model('documents', 'DocumentFolder')
    default_folders = [
        ('GENERAL', 'General'),
        ('POLICIES', 'Policies'),
        ('PROCEDURES', 'Procedures'),
        ('FORMS', 'Forms'),
        ('REPORTS', 'Reports'),
        ('TEMPLATES', 'Templates'),
    ]
    for key, name in default_folders:
        DocumentFolder.objects.get_or_create(key=key, defaults={'name': name})


def remove_default_folders(apps, schema_editor):
    DocumentFolder = apps.get_model('documents', 'DocumentFolder')
    DocumentFolder.objects.filter(key__in=[
        'GENERAL',
        'POLICIES',
        'PROCEDURES',
        'FORMS',
        'REPORTS',
        'TEMPLATES',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_document_section'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentFolder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(seed_default_folders, remove_default_folders),
    ]
