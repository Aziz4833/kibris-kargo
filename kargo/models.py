from django.db import models
from django.utils.text import slugify


class Sirket(models.Model):
    isim = models.CharField('Şirket ismi', max_length=120, unique=True)
    slug = models.SlugField('Endpoint', max_length=140, unique=True, blank=True, null=True)
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
