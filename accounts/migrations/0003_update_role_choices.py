from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_auditlog_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(
                choices=[
                    ('ADVISER', 'Adviser'),
                    ('PRESIDENT', 'President'),
                    ('VICE_PRESIDENT', 'Vice President'),
                    ('SECRETARY', 'Secretary'),
                    ('ASSISTANT_SECRETARY', 'Assistant Secretary'),
                    ('TREASURER', 'Treasurer'),
                    ('ASSISTANT_TREASURER', 'Assistant Treasurer'),
                    ('AUDITOR', 'Auditor'),
                    ('BUSINESS_MANAGER', 'Business Manager'),
                    ('PIO', 'PIO'),
                    ('ATHLETIC_MANAGER_MALE', 'Athletic Manager (Male)'),
                    ('ATHLETIC_MANAGER_FEMALE', 'Athletic Manager (Female)'),
                    ('BSCS_1A_REPRESENTATIVE', 'BSCS 1A Representative'),
                    ('BSCS_1B_REPRESENTATIVE', 'BSCS 1B Representative'),
                    ('BSCS_2A_REPRESENTATIVE', 'BSCS 2A Representative'),
                    ('BSCS_2B_REPRESENTATIVE', 'BSCS 2B Representative'),
                    ('BSCS_3A_REPRESENTATIVE', 'BSCS 3A Representative'),
                    ('BSCS_3B_REPRESENTATIVE', 'BSCS 3B Representative'),
                    ('BSCS_4A_REPRESENTATIVE', 'BSCS 4A Representative'),
                    ('BSCS_4B_REPRESENTATIVE', 'BSCS 4B Representative'),
                ],
                max_length=50,
                unique=True,
            ),
        ),
    ]
