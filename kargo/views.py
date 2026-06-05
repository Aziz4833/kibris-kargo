from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PanelGirisForm, SirketForm, UrunForm
from .models import Sirket, Urun


def anasayfa(request):
    sirketler = (
        Sirket.objects.filter(yayinda=True)
        .annotate(yayindaki_urun_sayisi=Count('urunler'))
    )
    toplam_urun = Urun.objects.filter(yayinda=True, sirket__yayinda=True).count()
    return render(
        request,
        'kargo/anasayfa.html',
        {
            'sirketler': sirketler,
            'toplam_urun': toplam_urun,
        },
    )


def sirket_detay(request, slug):
    sirket = get_object_or_404(Sirket, slug=slug, yayinda=True)
    urunler = sirket.urunler.filter(yayinda=True)
    return render(
        request,
        'kargo/sirket_detay.html',
        {
            'sirket': sirket,
            'urunler': urunler,
        },
    )


def urun_detay(request, slug, pk):
    sirket = get_object_or_404(Sirket, slug=slug, yayinda=True)
    urun = get_object_or_404(Urun, pk=pk, sirket=sirket, yayinda=True)
    return render(
        request,
        'kargo/urun_detay.html',
        {
            'sirket': sirket,
            'urun': urun,
        },
    )


def eski_sirket_detay(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk, yayinda=True)
    return redirect('sirket_detay', slug=sirket.slug, permanent=True)


def panel_giris(request):
    if request.user.is_authenticated and _panel_yetkili_mi(request.user):
        return redirect('panel')

    form = PanelGirisForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.user)
        return redirect('panel')

    return render(
        request,
        'kargo/panel_giris.html',
        {
            'form': form,
        },
    )


def panel_cikis(request):
    logout(request)
    return redirect('panel_giris')


def panel_yetkisi_gerekli(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not _panel_yetkili_mi(request.user):
            messages.error(request, 'Bu panele erişim yetkiniz yok.')
            logout(request)
            return redirect('panel_giris')
        return view_func(request, *args, **kwargs)

    return wrapper


@panel_yetkisi_gerekli
def panel(request):
    sirketler = Sirket.objects.annotate(urun_sayisi=Count('urunler')).order_by('-guncellenme_tarihi')
    taslak_sayisi = Sirket.objects.filter(yayinda=False).count()
    return render(
        request,
        'kargo/panel.html',
        {
            'sirketler': sirketler,
            'taslak_sayisi': taslak_sayisi,
            'yayindaki_sirket_sayisi': Sirket.objects.filter(yayinda=True).count(),
            'urun_sayisi': Urun.objects.count(),
        },
    )


@panel_yetkisi_gerekli
def sirket_detay_panel(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    urunler = sirket.urunler.all()
    return render(
        request,
        'kargo/panel_sirket_detay.html',
        {
            'sirket': sirket,
            'urunler': urunler,
        },
    )


@panel_yetkisi_gerekli
def sirket_form(request, pk=None):
    sirket = get_object_or_404(Sirket, pk=pk) if pk else None
    form = SirketForm(request.POST or None, request.FILES or None, instance=sirket)

    if request.method == 'POST' and form.is_valid():
        kayit = form.save()
        messages.success(request, f'{kayit.isim} şirketi kaydedildi.')
        return redirect('panel_sirket_detay', pk=kayit.pk)

    return render(
        request,
        'kargo/panel_sirket_form.html',
        {
            'form': form,
            'sirket': sirket,
        },
    )


@panel_yetkisi_gerekli
@require_POST
def sirket_yayinla(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    sirket.yayinda = True
    sirket.save(update_fields=['yayinda', 'guncellenme_tarihi'])
    messages.success(request, f'{sirket.isim} ana sayfaya eklendi.')
    return redirect('panel_sirket_detay', pk=sirket.pk)


@panel_yetkisi_gerekli
@require_POST
def sirket_yayindan_kaldir(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    sirket.yayinda = False
    sirket.save(update_fields=['yayinda', 'guncellenme_tarihi'])
    messages.success(request, f'{sirket.isim} ana sayfadan kaldırıldı.')
    return redirect('panel_sirket_detay', pk=sirket.pk)


@panel_yetkisi_gerekli
@require_POST
def sirket_sil(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    sirket_ismi = sirket.isim
    sirket.delete()
    messages.success(request, f'{sirket_ismi} şirketi ve bağlı ürünleri silindi.')
    return redirect('panel')


@panel_yetkisi_gerekli
def urun_form(request, sirket_pk=None, pk=None):
    sirket = get_object_or_404(Sirket, pk=sirket_pk) if sirket_pk else None
    urun = get_object_or_404(Urun, pk=pk) if pk else None
    form = UrunForm(request.POST or None, request.FILES or None, instance=urun)

    if request.method == 'POST' and form.is_valid():
        kayit = form.save(commit=False)
        if sirket is not None:
            kayit.sirket = sirket
        kayit.save()
        messages.success(request, f'{kayit.isim} ürünü kaydedildi.')
        return redirect('panel_sirket_detay', pk=kayit.sirket.pk)

    return render(
        request,
        'kargo/panel_urun_form.html',
        {
            'form': form,
            'sirket': sirket or urun.sirket,
            'urun': urun,
        },
    )


@panel_yetkisi_gerekli
@require_POST
def urun_sil(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    sirket_pk = urun.sirket.pk
    urun.delete()
    messages.success(request, 'Ürün silindi.')
    return redirect('panel_sirket_detay', pk=sirket_pk)


def _panel_yetkili_mi(user):
    return user.is_authenticated and user.email.lower() == settings.KARGO_ADMIN_EMAIL

# Create your views here.
