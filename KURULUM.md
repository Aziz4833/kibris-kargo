# Kurulum Rehberi

Bu dosya projeyi yeni bir laptopta sifirdan calistirmak icin gereken adimlari anlatir. Veritabani verisinin gelmesi zorunlu degildir; yeni cihazda temiz PostgreSQL ile baslatabilirsiniz.

## 1. Gerekli Programlar

Yeni cihazda sunlar kurulu olmali:

- Git
- Python 3.13 veya `runtime.txt` dosyasindaki Python surumu
- Docker Desktop
- VS Code veya tercih edilen editor

Kontrol komutlari:

```powershell
git --version
py --version
docker --version
docker compose version
```

## 2. Projeyi GitHub'dan Alma

```powershell
git clone https://github.com/Aziz4833/kibris-kargo.git
cd kibris-kargo
```

## 3. Sanal Ortam Olusturma

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

PowerShell script calistirmaya izin vermezse:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Sonra terminali kapatip tekrar acin ve sanal ortami yeniden aktif edin.

## 4. Env Dosyasi

`.env.example` dosyasini kopyalayip `.env` olusturun.

```powershell
Copy-Item .env.example .env
```

Local gelistirme icin `.env` icinde su mantik kullanilabilir:

```env
KARGO_DEBUG=True
SECRET_KEY=local-development-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=postgresql://kibris_kargo:kibris_kargo@127.0.0.1:5432/kibris_kargo
KARGO_ADMIN_EMAIL=admin@gmail.com
KARGO_ADMIN_PASSWORD=buraya-admin-sifresi-yazin
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_SSL_REDIRECT=False
```

Not: `.env` GitHub'a gitmez. Bu dogru davranistir.

## 5. PostgreSQL'i Baslatma

Docker Desktop acik olmalidir.

```powershell
docker compose up -d postgres
docker compose ps
```

`kibris_kargo_postgres` calisiyor gorunmelidir.

## 6. Migration Calistirma

```powershell
py manage.py migrate
```

Bu komut tablo yapisini olusturur. Eski verilerin gelmesi gerekmez.

## 7. Admin Hesabini Hazirlama

`.env` icindeki `KARGO_ADMIN_EMAIL` ve `KARGO_ADMIN_PASSWORD` degerlerine gore admin hesabi olusturulur veya guncellenir.

```powershell
py manage.py admin_hazirla
```

Bu komut ayni zamanda varsayilan sirket kategorilerini de hazirlar.

## 8. Siteyi Calistirma

```powershell
py manage.py runserver 127.0.0.1:8000
```

Tarayicida ac:

```text
http://127.0.0.1:8000/
```

Panel girisi:

```text
http://127.0.0.1:8000/panel/giris/
```

## 9. Test Calistirma

```powershell
py manage.py test
```

Beklenen sonuc: testler OK gecmeli.

## 10. Media Dosyalari Hakkinda

`media/` klasoru GitHub'a gitmez. Bu klasorde kullanicilarin yukledigi logo ve urun fotograflari tutulur.

Yeni cihazda:

- Veritabani temiz baslayabilir.
- Eski logo/fotograflar gelmez.
- Gerekirse eski cihazdan `media/` klasoru elle kopyalanabilir.

## 11. Onemli Dosyalar

Backend:

- `manage.py`: Django komutlarini calistirir.
- `kibris_kargo/settings.py`: Proje ayarlari, env, database, static/media ayarlari.
- `kibris_kargo/urls.py`: Ana URL yonlendirmeleri.
- `kargo/models.py`: Sirket, urun, satici yetkisi ve kategori modelleri.
- `kargo/forms.py`: Giris, kayit, sirket ve urun formlari.
- `kargo/views.py`: Sayfa mantigi ve yetki kontrolleri.
- `kargo/urls.py`: Uygulama URL'leri.
- `kargo/admin.py`: Django admin gorunumu.
- `kargo/management/commands/admin_hazirla.py`: Admin hesabi ve varsayilan kategorileri hazirlar.
- `kargo/migrations/`: Database tablo gecmisini tutar, silinmemeli.

Frontend:

- `kargo/templates/kargo/base.html`: Tum sayfalarin ana iskeleti, CSS/JS importlari.
- `kargo/templates/kargo/anasayfa.html`: Musterinin gordugu ana sayfa.
- `kargo/templates/kargo/sirket_detay.html`: Musterinin gordugu sirket vitrini.
- `kargo/templates/kargo/urun_detay.html`: Urun detay sayfasi.
- `kargo/templates/kargo/panel.html`: Admin/satici ana paneli.
- `kargo/templates/kargo/panel_sirket_form.html`: Sirket olusturma/duzenleme formu.
- `kargo/templates/kargo/panel_sirket_detay.html`: Sirket dashboard'u.
- `kargo/templates/kargo/panel_urun_form.html`: Urun ekleme/duzenleme formu.
- `kargo/templates/kargo/panel_giris.html`: Giris sayfasi.
- `kargo/templates/kargo/kayit.html`: Kayit sayfasi.
- `static/kargo/styles.css`: Tum ana tasarim.
- `static/kargo/app.js`: Gorsel onizleme, urun sablonlari, dinamik ozellik alanlari ve vergi hesaplama.

Deploy/local yardimci dosyalari:

- `requirements.txt`: Python paketleri.
- `docker-compose.yml`: Local PostgreSQL servisi.
- `Procfile`: Deploy server baslatma komutu.
- `build.sh`: Deploy build adimlari.
- `runtime.txt`: Deploy Python surumu.
- `.env.example`: Env sablonu.
- `.gitignore`: GitHub'a gitmemesi gereken dosyalar.
- `DEPLOY.md`: Deploy notlari.

## 12. Sik Karsilasilan Sorunlar

Docker calismiyorsa:

```powershell
docker compose ps
```

Docker API hatasi aliyorsaniz Docker Desktop'i acin ve tekrar deneyin.

Database baglanti hatasi varsa:

- Docker Desktop acik mi?
- `docker compose up -d postgres` calisti mi?
- `.env` icindeki `DATABASE_URL` dogru mu?

Admin girisi olmuyorsa:

```powershell
py manage.py admin_hazirla
```

CSS eski gorunuyorsa:

- Tarayicida hard refresh yapin: `Ctrl + F5`
- `base.html` icindeki static versiyon parametresi degistirilebilir.
