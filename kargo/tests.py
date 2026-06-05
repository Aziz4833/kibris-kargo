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
        sirket = Sirket.objects.create(isim='Örnek Firma', yayinda=True)
        Urun.objects.create(
            sirket=sirket,
            isim='Kahve Makinesi',
            aciklama='Filtre kahve makinesi.',
            cikis_yeri='İstanbul',
            kargonun_gelecegi_yer='Girne',
            kargo_durumu='yolda',
            takip_kodu='ABC123',
            fiyat='2500.00',
        )

        response = self.client.get(reverse('anasayfa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Örnek Firma')
        self.assertNotContains(response, 'Kahve Makinesi')

        detay_response = self.client.get(reverse('sirket_detay', args=[sirket.slug]))

        self.assertEqual(detay_response.status_code, 200)
        self.assertContains(detay_response, 'Kahve Makinesi')
        self.assertContains(detay_response, 'ABC123')
        self.assertContains(detay_response, 'Yolda')
        self.assertEqual(sirket.slug, 'ornek-firma')

    def test_panel_yetkisiz_kullaniciya_kapali(self):
        self.client.login(username='baska@example.com', password='GuvenliSifre123')

        response = self.client.get(reverse('panel'), follow=True)

        self.assertRedirects(response, reverse('panel_giris'))
        self.assertContains(response, 'Çalışan girişi')

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

    def test_sirket_urunleriyle_silinebilir(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')
        sirket = Sirket.objects.create(isim='Silinecek Firma', yayinda=True)
        Urun.objects.create(
            sirket=sirket,
            isim='Silinecek Ürün',
            aciklama='Silme testi.',
            kargonun_gelecegi_yer='Lefkoşa',
            fiyat='100.00',
        )

        response = self.client.post(reverse('sirket_sil', args=[sirket.pk]))

        self.assertRedirects(response, reverse('panel'))
        self.assertFalse(Sirket.objects.filter(pk=sirket.pk).exists())
        self.assertFalse(Urun.objects.filter(isim='Silinecek Ürün').exists())

# Create your tests here.
