from django.db import models
from django.conf import settings
from django.utils.text import slugify


class SaticiYetkisi(models.Model):
    email = models.EmailField('Satıcı e-postası', unique=True)
    aktif = models.BooleanField('Aktif', default=True)
    veren = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Yetkiyi veren',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='verdigi_satici_yetkileri',
    )
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Satıcı yetkisi'
        verbose_name_plural = 'Satıcı yetkileri'
        ordering = ['email']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)


class SirketKategorisi(models.Model):
    ad = models.CharField('Kategori adı', max_length=80, unique=True)
    slug = models.SlugField('Kategori endpointi', max_length=100, unique=True, blank=True, null=True)
    aciklama = models.TextField('Açıklama', blank=True)
    aktif = models.BooleanField('Aktif', default=True)
    sira = models.PositiveIntegerField('Sıra', default=100)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Şirket kategorisi'
        verbose_name_plural = 'Şirket kategorileri'
        ordering = ['sira', 'ad']

    def __str__(self):
        return self.ad

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.ad) or 'kategori'
            slug = base_slug
            counter = 2
            while SirketKategorisi.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Sirket(models.Model):
    sahip = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Şirket sahibi',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sirketleri',
    )
    isim = models.CharField('Şirket ismi', max_length=120, unique=True)
    slug = models.SlugField('Endpoint', max_length=140, unique=True, blank=True, null=True)
    kategoriler = models.ManyToManyField(
        SirketKategorisi,
        verbose_name='Şirket kategorileri',
        blank=True,
        related_name='sirketler',
    )
    ozel_kategori = models.CharField('Özel kategoriler', max_length=240, blank=True)
    isletme_tipi = models.CharField('İşletme tipi', max_length=120, blank=True)
    logo = models.ImageField('Logo', upload_to='sirket_logolari/', blank=True)
    aciklama = models.TextField('Kısa açıklama', blank=True)
    merkez = models.CharField('Merkez / şehir', max_length=160, blank=True)
    teslimat_bolgeleri = models.TextField('Teslimat bölgeleri', blank=True)
    iletisim_email = models.EmailField('İletişim e-postası', blank=True)
    telefon = models.CharField('Telefon', max_length=40, blank=True)
    web_sitesi = models.URLField('Web sitesi', blank=True)
    yayinda = models.BooleanField('Ana sayfada yayınla', default=False)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Şirket'
        verbose_name_plural = 'Şirketler'
        ordering = ['isim']

    def __str__(self):
        return self.isim

    @property
    def gorunen_kategori(self):
        kategori_adlari = []
        if self.pk:
            kategori_adlari = list(self.kategoriler.values_list('ad', flat=True))
        if self.ozel_kategori:
            kategori_adlari.extend(
                kategori.strip()
                for kategori in self.ozel_kategori.split(',')
                if kategori.strip()
            )
        return ', '.join(kategori_adlari)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.isim) or 'sirket'
            slug = base_slug
            counter = 2
            while Sirket.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Urun(models.Model):
    sirket = models.ForeignKey(
        Sirket,
        verbose_name='Şirket',
        related_name='urunler',
        on_delete=models.CASCADE,
    )
    isim = models.CharField('Ürün ismi', max_length=160)
    kategori = models.CharField('Kategori', max_length=80, blank=True)
    fotograf = models.ImageField('Ürün fotoğrafı', upload_to='urun_fotograflari/', blank=True)
    aciklama = models.TextField('Açıklama')
    cikis_yeri = models.CharField('Çıkış yeri', max_length=180, blank=True)
    kargonun_gelecegi_yer = models.CharField('Kargonun geleceği yer', max_length=180)
    adet = models.PositiveIntegerField('Adet', default=1)
    fiyat = models.DecimalField('Fiyat', max_digits=10, decimal_places=2)
    vergi_orani = models.DecimalField('Vergi oranı (%)', max_digits=5, decimal_places=2, default=0)
    ozellikler = models.JSONField('Ek özellikler', default=dict, blank=True)
    yayinda = models.BooleanField('Ürünü göster', default=True)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-olusturulma_tarihi']

    def __str__(self):
        return f'{self.isim} - {self.sirket.isim}'
