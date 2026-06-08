from django.contrib import admin

from .models import SaticiYetkisi, Sirket, SirketKategorisi, Urun


class UrunInline(admin.TabularInline):
    model = Urun
    extra = 1


@admin.register(Sirket)
class SirketAdmin(admin.ModelAdmin):
    list_display = ('isim', 'kategori_listesi', 'ozel_kategori', 'sahip', 'yayinda', 'guncellenme_tarihi')
    list_filter = ('yayinda', 'kategoriler')
    search_fields = ('isim', 'ozel_kategori', 'sahip__email')
    inlines = [UrunInline]

    def kategori_listesi(self, obj):
        return obj.gorunen_kategori

    kategori_listesi.short_description = 'Kategoriler'


@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('isim', 'sirket', 'kategori', 'fiyat', 'kargonun_gelecegi_yer', 'yayinda')
    list_filter = ('yayinda', 'kategori', 'sirket')
    search_fields = ('isim', 'aciklama', 'kargonun_gelecegi_yer', 'sirket__isim')


@admin.register(SaticiYetkisi)
class SaticiYetkisiAdmin(admin.ModelAdmin):
    list_display = ('email', 'aktif', 'veren', 'guncellenme_tarihi')
    list_filter = ('aktif',)
    search_fields = ('email',)


@admin.register(SirketKategorisi)
class SirketKategorisiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aktif', 'sira', 'guncellenme_tarihi')
    list_filter = ('aktif',)
    search_fields = ('ad', 'aciklama')

# Register your models here.
