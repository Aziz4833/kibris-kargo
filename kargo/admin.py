from django.contrib import admin

from .models import Sirket, Urun


class UrunInline(admin.TabularInline):
    model = Urun
    extra = 1


@admin.register(Sirket)
class SirketAdmin(admin.ModelAdmin):
    list_display = ('isim', 'yayinda', 'guncellenme_tarihi')
    list_filter = ('yayinda',)
    search_fields = ('isim',)
    inlines = [UrunInline]


@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('isim', 'sirket', 'fiyat', 'kargonun_gelecegi_yer', 'yayinda')
    list_filter = ('yayinda', 'sirket')
    search_fields = ('isim', 'aciklama', 'kargonun_gelecegi_yer', 'sirket__isim')

# Register your models here.
