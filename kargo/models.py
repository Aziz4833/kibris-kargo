from django.db import models


class Sirket(models.Model):
    isim = models.CharField('Şirket ismi', max_length=120, unique=True)
    logo = models.ImageField('Logo', upload_to='sirket_logolari/', blank=True)
    aciklama = models.TextField('Kısa açıklama', blank=True)
    yayinda = models.BooleanField('Ana sayfada yayınla', default=False)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Şirket'
        verbose_name_plural = 'Şirketler'
        ordering = ['isim']

    def __str__(self):
        return self.isim


class Urun(models.Model):
    sirket = models.ForeignKey(
        Sirket,
        verbose_name='Şirket',
        related_name='urunler',
        on_delete=models.CASCADE,
    )
    isim = models.CharField('Ürün ismi', max_length=160)
    fotograf = models.ImageField('Ürün fotoğrafı', upload_to='urun_fotograflari/', blank=True)
    aciklama = models.TextField('Açıklama')
    kargonun_gelecegi_yer = models.CharField('Kargonun geleceği yer', max_length=180)
    fiyat = models.DecimalField('Fiyat', max_digits=10, decimal_places=2)
    yayinda = models.BooleanField('Ürünü göster', default=True)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-olusturulma_tarihi']

    def __str__(self):
        return f'{self.isim} - {self.sirket.isim}'
