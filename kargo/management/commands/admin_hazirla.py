from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Yetkili panel hesabını oluşturur veya günceller.'

    def add_arguments(self, parser):
        parser.add_argument('--password', help='Yetkili panel hesabı şifresi. Verilmezse KARGO_ADMIN_PASSWORD okunur.')

    def handle(self, *args, **options):
        password = options['password'] or settings.KARGO_ADMIN_PASSWORD
        if not password:
            raise CommandError('Admin sifresi icin --password verin veya KARGO_ADMIN_PASSWORD ayarlayin.')

        User = get_user_model()
        email = settings.KARGO_ADMIN_EMAIL
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.username = email
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = 'olusturuldu' if created else 'guncellendi'
        self.stdout.write(self.style.SUCCESS(f'{email} panel hesabi {action}.'))
