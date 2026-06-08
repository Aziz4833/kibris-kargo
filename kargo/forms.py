import json

from django import forms
from django.contrib.auth import authenticate, get_user_model

from .models import SaticiYetkisi, Sirket, SirketKategorisi, Urun


class KayitForm(forms.Form):
    email = forms.EmailField(label='E-posta')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)
    password_tekrar = forms.CharField(label='Şifre tekrar', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Bu e-posta ile kayıtlı bir hesap var.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_tekrar = cleaned_data.get('password_tekrar')
        if password and password_tekrar and password != password_tekrar:
            raise forms.ValidationError('Şifreler aynı olmalı.')
        return cleaned_data

    def save(self):
        User = get_user_model()
        email = self.cleaned_data['email']
        return User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password'],
        )


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


class SaticiYetkisiForm(forms.ModelForm):
    class Meta:
        model = SaticiYetkisi
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'satici@example.com'}),
        }

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class SirketKategorisiForm(forms.ModelForm):
    class Meta:
        model = SirketKategorisi
        fields = ['ad', 'aciklama']
        widgets = {
            'ad': forms.TextInput(attrs={'placeholder': 'Moda, teknoloji, ev yaşam...'}),
            'aciklama': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Bu kategori hangi şirketleri kapsar?'}),
        }


class SirketForm(forms.ModelForm):
    class Meta:
        model = Sirket
        fields = [
            'isim',
            'logo',
            'aciklama',
        ]
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 3}),
        }


class UrunForm(forms.ModelForm):
    ozellikler_json = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Urun
        fields = [
            'isim',
            'kategori',
            'fotograf',
            'aciklama',
            'cikis_yeri',
            'kargonun_gelecegi_yer',
            'adet',
            'fiyat',
            'vergi_orani',
            'yayinda',
        ]
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
            'adet': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'fiyat': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'vergi_orani': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *args, patron_mu=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not patron_mu:
            self.fields.pop('vergi_orani', None)
        if self.instance and self.instance.pk:
            self.fields['ozellikler_json'].initial = json.dumps(
                self.instance.ozellikler or {},
                ensure_ascii=False,
            )

    def clean_ozellikler_json(self):
        raw_value = self.cleaned_data.get('ozellikler_json') or '{}'
        try:
            data = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError('Ek özellikler okunamadı.') from exc

        if not isinstance(data, dict):
            raise forms.ValidationError('Ek özellikler anahtar ve değer şeklinde olmalı.')

        temiz_data = {}
        for key, value in data.items():
            temiz_key = str(key).strip()
            temiz_value = str(value).strip()
            if temiz_key and temiz_value:
                temiz_data[temiz_key[:80]] = temiz_value[:240]
        return temiz_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.ozellikler = self.cleaned_data.get('ozellikler_json', {})
        if commit:
            instance.save()
            self.save_m2m()
        return instance
