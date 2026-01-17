from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Initialize default roles'

    def handle(self, *args, **kwargs):
        roles = [
            (Role.ADVISER, 'Adviser with full system access'),
            (Role.PRESIDENT, 'President with broad access to documents and reports'),
            (Role.VICE_PRESIDENT, 'Access governed by Adviser and President'),
            (Role.SECRETARY, 'Access governed by Adviser and President'),
            (Role.ASSISTANT_SECRETARY, 'Access governed by Adviser and President'),
            (Role.TREASURER, 'Access governed by Adviser and President'),
            (Role.ASSISTANT_TREASURER, 'Access governed by Adviser and President'),
            (Role.AUDITOR, 'Access governed by Adviser and President'),
            (Role.BUSINESS_MANAGER, 'Access governed by Adviser and President'),
            (Role.PIO, 'Access governed by Adviser and President'),
            (Role.ATHLETIC_MANAGER_MALE, 'Access governed by Adviser and President'),
            (Role.ATHLETIC_MANAGER_FEMALE, 'Access governed by Adviser and President'),
            (Role.BSCS_1A_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_1B_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_2A_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_2B_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_3A_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_3B_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_4A_REPRESENTATIVE, 'Access governed by Adviser and President'),
            (Role.BSCS_4B_REPRESENTATIVE, 'Access governed by Adviser and President'),
        ]
        
        for role_name, description in roles:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role_name}')
                )
