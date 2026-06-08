from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from kargo.models import SirketKategorisi


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

        kategoriler = [
            ('Moda', 'Giyim, ayakkabı ve aksesuar satan işletmeler.'),
            ('Teknoloji', 'Elektronik, bilgisayar, telefon ve aksesuar ürünleri.'),
            ('Ev ve Yaşam', 'Ev, dekorasyon, mutfak ve yaşam ürünleri.'),
            ('Kozmetik', 'Bakım, kozmetik ve kişisel ürünler.'),
            ('Market', 'Gıda, temel ihtiyaç ve günlük tüketim ürünleri.'),
            ('Spor', 'Spor ekipmanları, outdoor ve hobi ürünleri.'),
            ('Kitap ve Kırtasiye', 'Kitap, kırtasiye ve eğitim ürünleri.'),
            ('Diğer', 'Özel veya karma ürün satan işletmeler.'),
        ]
        for sira, (ad, aciklama) in enumerate(kategoriler, start=10):
            SirketKategorisi.objects.get_or_create(
                ad=ad,
                defaults={'aciklama': aciklama, 'sira': sira},
            )

        action = 'olusturuldu' if created else 'guncellendi'
        self.stdout.write(self.style.SUCCESS(f'{email} panel hesabi {action}.'))
        self.stdout.write(self.style.SUCCESS('Varsayilan sirket kategorileri hazir.'))
