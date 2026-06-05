from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Sirket, Urun


class KargoAkisTestleri(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username=settings.KARGO_ADMIN_EMAIL,
            email=settings.KARGO_ADMIN_EMAIL,
            password='GuvenliSifre123',
        )
        self.baska_user = User.objects.create_user(
            username='baska@example.com',
            email='baska@example.com',
            password='GuvenliSifre123',
        )

    def test_ana_sayfa_yayindaki_sirketi_gosterir(self):
        sirket = Sirket.objects.create(isim='Trendyol', yayinda=True)
        Urun.objects.create(
            sirket=sirket,
            isim='Kahve Makinesi',
            aciklama='Filtre kahve makinesi.',
            kargonun_gelecegi_yer='Girne',
            fiyat='2500.00',
        )

        response = self.client.get(reverse('anasayfa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trendyol')
        self.assertContains(response, 'Kahve Makinesi')

    def test_panel_yetkisiz_kullaniciya_kapali(self):
        self.client.login(username='baska@example.com', password='GuvenliSifre123')

        response = self.client.get(reverse('panel'), follow=True)

        self.assertRedirects(response, reverse('panel_giris'))
        self.assertContains(response, 'Bu panel sadece')

    def test_yetkili_kullanici_paneli_acar(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')

        response = self.client.get(reverse('panel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Şirket ve ürün paneli')

    def test_sirket_siteye_eklenebilir(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')
        sirket = Sirket.objects.create(isim='Amazon')

        response = self.client.post(reverse('sirket_yayinla', args=[sirket.pk]))

        sirket.refresh_from_db()
        self.assertRedirects(response, reverse('panel_sirket_detay', args=[sirket.pk]))
        self.assertTrue(sirket.yayinda)

# Create your tests here.
