from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    KayitForm,
    PanelGirisForm,
    SaticiYetkisiForm,
    SirketForm,
    SirketKategorisiForm,
    UrunForm,
)
from .models import SaticiYetkisi, Sirket, SirketKategorisi, Urun


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
            'patron_mu': _patron_mu(request.user),
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


def kayit(request):
    if request.user.is_authenticated:
        return redirect('panel' if _panel_yetkili_mi(request.user) else 'anasayfa')

    form = KayitForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        if _panel_yetkili_mi(user):
            messages.success(request, 'Hesabınız açıldı. Şirket paneline geçebilirsiniz.')
            return redirect('panel')
        messages.success(request, 'Hesabınız açıldı.')
        return redirect('anasayfa')

    return render(
        request,
        'kargo/kayit.html',
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
            return redirect('anasayfa')
        return view_func(request, *args, **kwargs)

    return wrapper


def patron_yetkisi_gerekli(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not _patron_mu(request.user):
            return HttpResponseForbidden('Bu işlem için patron yetkisi gerekir.')
        return view_func(request, *args, **kwargs)

    return wrapper


@panel_yetkisi_gerekli
def panel(request):
    sirketler = _erisilebilir_sirketler(request.user).annotate(
        urun_sayisi=Count('urunler'),
    ).order_by('-guncellenme_tarihi')
    taslak_sayisi = sirketler.filter(yayinda=False).count()
    yetki_formu = SaticiYetkisiForm()
    kategori_formu = SirketKategorisiForm()
    kategoriler = SirketKategorisi.objects.none()
    satici_yetkileri = SaticiYetkisi.objects.none()
    if _patron_mu(request.user):
        satici_yetkileri = SaticiYetkisi.objects.all()
        kategoriler = SirketKategorisi.objects.all()

    return render(
        request,
        'kargo/panel.html',
        {
            'sirketler': sirketler,
            'taslak_sayisi': taslak_sayisi,
            'yayindaki_sirket_sayisi': sirketler.filter(yayinda=True).count(),
            'urun_sayisi': Urun.objects.filter(sirket__in=sirketler).count(),
            'patron_mu': _patron_mu(request.user),
            'yetki_formu': yetki_formu,
            'satici_yetkileri': satici_yetkileri,
            'kategori_formu': kategori_formu,
            'kategoriler': kategoriler,
        },
    )


@patron_yetkisi_gerekli
@require_POST
def satici_yetkisi_ekle(request):
    form = SaticiYetkisiForm(request.POST)
    if form.is_valid():
        yetki = form.save(commit=False)
        yetki.veren = request.user
        yetki.aktif = True
        yetki.save()
        messages.success(request, f'{yetki.email} satıcı olarak yetkilendirildi.')
    else:
        messages.error(request, 'Satıcı e-postası kaydedilemedi.')
    return redirect('panel')


@patron_yetkisi_gerekli
@require_POST
def satici_yetkisi_sil(request, pk):
    yetki = get_object_or_404(SaticiYetkisi, pk=pk)
    email = yetki.email
    yetki.delete()
    messages.success(request, f'{email} satıcı yetkisi kaldırıldı.')
    return redirect('panel')


@patron_yetkisi_gerekli
@require_POST
def sirket_kategorisi_ekle(request):
    form = SirketKategorisiForm(request.POST)
    if form.is_valid():
        kategori = form.save()
        messages.success(request, f'{kategori.ad} şirket kategorisi eklendi.')
    else:
        messages.error(request, 'Şirket kategorisi kaydedilemedi.')
    return redirect('panel')


@patron_yetkisi_gerekli
@require_POST
def sirket_kategorisi_sil(request, pk):
    kategori = get_object_or_404(SirketKategorisi, pk=pk)
    ad = kategori.ad
    kategori.delete()
    messages.success(request, f'{ad} şirket kategorisi silindi.')
    return redirect('panel')


@panel_yetkisi_gerekli
def sirket_detay_panel(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    if not _sirket_erisebilir_mi(request.user, sirket):
        return HttpResponseForbidden('Bu şirketi yönetemezsiniz.')
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
    if sirket is not None and not _sirket_erisebilir_mi(request.user, sirket):
        return HttpResponseForbidden('Bu şirketi düzenleyemezsiniz.')

    form = SirketForm(request.POST or None, request.FILES or None, instance=sirket)

    if request.method == 'POST' and form.is_valid():
        kayit = form.save(commit=False)
        if kayit.pk is None and not _patron_mu(request.user):
            kayit.sahip = request.user
        elif kayit.pk is None and kayit.sahip_id is None:
            kayit.sahip = request.user
        kayit.save()
        form.save_m2m()
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
    if not _sirket_erisebilir_mi(request.user, sirket):
        return HttpResponseForbidden('Bu şirketi yayınlayamazsınız.')
    sirket.yayinda = True
    sirket.save(update_fields=['yayinda', 'guncellenme_tarihi'])
    messages.success(request, f'{sirket.isim} ana sayfaya eklendi.')
    return redirect('panel_sirket_detay', pk=sirket.pk)


@panel_yetkisi_gerekli
@require_POST
def sirket_yayindan_kaldir(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    if not _sirket_erisebilir_mi(request.user, sirket):
        return HttpResponseForbidden('Bu şirketi yayından kaldıramazsınız.')
    sirket.yayinda = False
    sirket.save(update_fields=['yayinda', 'guncellenme_tarihi'])
    messages.success(request, f'{sirket.isim} ana sayfadan kaldırıldı.')
    return redirect('panel_sirket_detay', pk=sirket.pk)


@panel_yetkisi_gerekli
@require_POST
def sirket_sil(request, pk):
    sirket = get_object_or_404(Sirket, pk=pk)
    if not _sirket_erisebilir_mi(request.user, sirket):
        return HttpResponseForbidden('Bu şirketi silemezsiniz.')
    sirket_ismi = sirket.isim
    sirket.delete()
    messages.success(request, f'{sirket_ismi} şirketi ve bağlı ürünleri silindi.')
    return redirect('panel')


@panel_yetkisi_gerekli
def urun_form(request, sirket_pk=None, pk=None):
    sirket = get_object_or_404(Sirket, pk=sirket_pk) if sirket_pk else None
    urun = get_object_or_404(Urun, pk=pk) if pk else None
    hedef_sirket = sirket or urun.sirket
    if not _sirket_erisebilir_mi(request.user, hedef_sirket):
        return HttpResponseForbidden('Bu ürünleri yönetemezsiniz.')

    form = UrunForm(
        request.POST or None,
        request.FILES or None,
        instance=urun,
        patron_mu=_patron_mu(request.user),
    )

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
            'sirket': hedef_sirket,
            'urun': urun,
            'patron_mu': _patron_mu(request.user),
        },
    )


@panel_yetkisi_gerekli
@require_POST
def urun_sil(request, pk):
    urun = get_object_or_404(Urun, pk=pk)
    if not _sirket_erisebilir_mi(request.user, urun.sirket):
        return HttpResponseForbidden('Bu ürünü silemezsiniz.')
    sirket_pk = urun.sirket.pk
    urun.delete()
    messages.success(request, 'Ürün silindi.')
    return redirect('panel_sirket_detay', pk=sirket_pk)


def _panel_yetkili_mi(user):
    return _patron_mu(user) or _satici_mi(user)


def _patron_mu(user):
    return (
        user.is_authenticated
        and (
            user.email.lower() == settings.KARGO_ADMIN_EMAIL
            or user.is_superuser
        )
    )


def _satici_mi(user):
    if not user.is_authenticated or not user.email:
        return False
    return SaticiYetkisi.objects.filter(email__iexact=user.email, aktif=True).exists()


def _erisilebilir_sirketler(user):
    if _patron_mu(user):
        return Sirket.objects.all()
    return Sirket.objects.filter(sahip=user)


def _sirket_erisebilir_mi(user, sirket):
    if _patron_mu(user):
        return True
    return _satici_mi(user) and sirket.sahip_id == user.id

# Create your views here.
