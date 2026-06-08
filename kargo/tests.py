from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SaticiYetkisi, Sirket, SirketKategorisi, Urun


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
        self.kategori, _ = SirketKategorisi.objects.get_or_create(
            ad='Moda',
            defaults={'aciklama': 'Giyim ve aksesuar.'},
        )
        self.ikinci_kategori, _ = SirketKategorisi.objects.get_or_create(
            ad='Teknoloji',
            defaults={'aciklama': 'Elektronik ürünler.'},
        )

    def test_ana_sayfa_yayindaki_sirketi_gosterir(self):
        sirket = Sirket.objects.create(isim='Örnek Firma', yayinda=True)
        Urun.objects.create(
            sirket=sirket,
            isim='Kahve Makinesi',
            aciklama='Filtre kahve makinesi.',
            cikis_yeri='İstanbul',
            kargonun_gelecegi_yer='Girne',
            adet=2,
            fiyat='2500.00',
            kategori='Ev',
            ozellikler={'Renk': 'Siyah'},
        )

        response = self.client.get(reverse('anasayfa'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Örnek Firma')
        self.assertNotContains(response, 'Kahve Makinesi')

        detay_response = self.client.get(reverse('sirket_detay', args=[sirket.slug]))

        self.assertEqual(detay_response.status_code, 200)
        self.assertContains(detay_response, 'Kahve Makinesi')
        self.assertContains(detay_response, 'İstanbul')
        self.assertContains(detay_response, 'Girne')
        self.assertEqual(sirket.slug, 'ornek-firma')

        urun = Urun.objects.get(isim='Kahve Makinesi')
        urun_response = self.client.get(reverse('urun_detay', args=[sirket.slug, urun.pk]))

        self.assertEqual(urun_response.status_code, 200)
        self.assertContains(urun_response, 'Filtre kahve makinesi.')
        self.assertContains(urun_response, 'Renk')
        self.assertContains(urun_response, 'Siyah')

    def test_panel_yetkisiz_kullaniciya_kapali(self):
        self.client.login(username='baska@example.com', password='GuvenliSifre123')

        response = self.client.get(reverse('panel'), follow=True)

        self.assertRedirects(response, reverse('anasayfa'))
        self.assertContains(response, 'Bu panele erişim yetkiniz yok.')

    def test_yetkili_kullanici_paneli_acar(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')

        response = self.client.get(reverse('panel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patron paneli')

    def test_patron_satici_yetkisi_verebilir(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')

        response = self.client.post(
            reverse('satici_yetkisi_ekle'),
            {'email': 'satici@example.com'},
        )

        self.assertRedirects(response, reverse('panel'))
        self.assertTrue(SaticiYetkisi.objects.filter(email='satici@example.com').exists())

    def test_satici_sadece_kendi_sirketini_yonetir(self):
        User = get_user_model()
        satici = User.objects.create_user(
            username='satici@example.com',
            email='satici@example.com',
            password='GuvenliSifre123',
        )
        SaticiYetkisi.objects.create(email='satici@example.com')
        baska_sirket = Sirket.objects.create(isim='Başka Firma', sahip=self.admin)
        self.client.login(username=satici.username, password='GuvenliSifre123')

        response = self.client.post(
            reverse('sirket_yeni'),
            {
                'isim': 'Satıcı Firması',
                'aciklama': 'Kendi vitrini',
            },
        )

        sirket = Sirket.objects.get(isim='Satıcı Firması')
        self.assertRedirects(response, reverse('panel_sirket_detay', args=[sirket.pk]))
        self.assertEqual(sirket.sahip, satici)
        self.assertEqual(self.client.get(reverse('panel_sirket_detay', args=[baska_sirket.pk])).status_code, 403)

    def test_patron_sirket_kategorisi_ekleyebilir(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')

        response = self.client.post(
            reverse('sirket_kategorisi_ekle'),
            {'ad': 'Oyuncak', 'aciklama': 'Çocuk ve oyuncak ürünleri.'},
        )

        self.assertRedirects(response, reverse('panel'))
        self.assertTrue(SirketKategorisi.objects.filter(ad='Oyuncak').exists())

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

    def test_urun_ozel_alanlari_kaydedilir(self):
        self.client.login(username=settings.KARGO_ADMIN_EMAIL, password='GuvenliSifre123')
        sirket = Sirket.objects.create(isim='Alan Testi', sahip=self.admin)

        response = self.client.post(
            reverse('urun_yeni', args=[sirket.pk]),
            {
                'isim': 'Spor Ayakkabı',
                'kategori': 'Ayakkabı',
                'aciklama': 'Rahat taban.',
                'cikis_yeri': 'İstanbul',
                'kargonun_gelecegi_yer': 'Lefkoşa',
                'adet': '4',
                'fiyat': '1200.00',
                'vergi_orani': '20.00',
                'ozellikler_json': '{"Numara":"42","Renk":"Beyaz"}',
                'yayinda': 'on',
            },
        )

        urun = Urun.objects.get(isim='Spor Ayakkabı')
        self.assertRedirects(response, reverse('panel_sirket_detay', args=[sirket.pk]))
        self.assertEqual(urun.ozellikler['Numara'], '42')
        self.assertEqual(urun.kategori, 'Ayakkabı')
        self.assertEqual(str(urun.vergi_orani), '20.00')

    def test_satici_vergi_oranini_degistiremez(self):
        User = get_user_model()
        satici = User.objects.create_user(
            username='vergi-satici@example.com',
            email='vergi-satici@example.com',
            password='GuvenliSifre123',
        )
        SaticiYetkisi.objects.create(email='vergi-satici@example.com')
        sirket = Sirket.objects.create(isim='Vergi Test Firma', sahip=satici)
        urun = Urun.objects.create(
            sirket=sirket,
            isim='Saat',
            aciklama='Kol saati.',
            kargonun_gelecegi_yer='Lefkoşa',
            fiyat='900.00',
            vergi_orani='18.00',
        )
        self.client.login(username=satici.username, password='GuvenliSifre123')

        response = self.client.post(
            reverse('urun_duzenle', args=[urun.pk]),
            {
                'isim': 'Saat',
                'kategori': 'Aksesuar',
                'aciklama': 'Kol saati.',
                'cikis_yeri': '',
                'kargonun_gelecegi_yer': 'Lefkoşa',
                'adet': '1',
                'fiyat': '950.00',
                'vergi_orani': '0.00',
                'ozellikler_json': '{}',
                'yayinda': 'on',
            },
        )

        urun.refresh_from_db()
        self.assertRedirects(response, reverse('panel_sirket_detay', args=[sirket.pk]))
        self.assertEqual(str(urun.vergi_orani), '18.00')
        self.assertEqual(str(urun.fiyat), '950.00')

# Create your tests here.
