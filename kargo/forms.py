from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

from .models import Sirket, Urun


class PanelGirisForm(forms.Form):
    email = forms.EmailField(label='E-posta')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').strip().lower()
        password = cleaned_data.get('password')

        if email and email != settings.KARGO_ADMIN_EMAIL:
            raise forms.ValidationError('Bu panele sadece yetkili e-posta adresi giriş yapabilir.')

        if email and password:
            User = get_user_model()
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None

            username = user.get_username() if user else email
            self.user = authenticate(self.request, username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('E-posta veya şifre hatalı.')
            if not self.user.is_active:
                raise forms.ValidationError('Bu hesap aktif değil.')

        return cleaned_data


class SirketForm(forms.ModelForm):
    class Meta:
        model = Sirket
        fields = ['isim', 'logo', 'aciklama']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 3}),
        }


class UrunForm(forms.ModelForm):
    class Meta:
        model = Urun
        fields = [
            'isim',
            'fotograf',
            'aciklama',
            'cikis_yeri',
            'kargonun_gelecegi_yer',
            'kargo_durumu',
            'takip_kodu',
            'siparis_tarihi',
            'tahmini_gelis_tarihi',
            'adet',
            'paket_agirligi',
            'kargo_notu',
            'fiyat',
            'yayinda',
        ]
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
            'siparis_tarihi': forms.DateInput(attrs={'type': 'date'}),
            'tahmini_gelis_tarihi': forms.DateInput(attrs={'type': 'date'}),
            'adet': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'paket_agirligi': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'kargo_notu': forms.Textarea(attrs={'rows': 3}),
            'fiyat': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }
