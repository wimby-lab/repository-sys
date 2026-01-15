from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Initialize default roles'

    def handle(self, *args, **kwargs):
        roles = [
            (Role.ADMIN, 'Administrator with full system access'),
            (Role.MANAGER, 'Manager with document management capabilities'),
            (Role.USER, 'Regular user with basic access'),
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
