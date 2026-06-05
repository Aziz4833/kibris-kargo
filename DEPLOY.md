# Deploy Kontrol Listesi

## 1. GitHub

1. `git init`
2. `git add .`
3. `git commit -m "ilk surum"`
4. GitHub'da boş repo açın.
5. `git remote add origin <repo-url>`
6. `git push -u origin main`

## 2. Hosting

Django için PostgreSQL destekleyen bir platform seçin. Render, Railway, Fly.io veya benzeri bir servis uygundur.

Bu proje SQLite fallback kullanmaz. Hosting ortamında mutlaka `DATABASE_URL` PostgreSQL bağlantısı ayarlanmalıdır.

Build komutu:

```bash
bash build.sh
```

Start komutu:

```bash
gunicorn kibris_kargo.wsgi:application
```

## 3. Ortam değişkenleri

`.env.example` dosyasındaki değerleri platformun Environment Variables bölümüne girin. `SECRET_KEY` rastgele, uzun ve gizli olmalı. `DATABASE_URL` platformun verdiği PostgreSQL bağlantısı olmalı.

## 4. Medya dosyaları

Logo ve ürün fotoğrafları kalıcı depolama ister. Hosting platformunda persistent disk açın veya daha sonra S3/Cloudinary entegrasyonu ekleyin.

## 5. İlk admin

Deploy tamamlandıktan sonra platformun shell/console alanında:

```bash
python manage.py admin_hazirla --password "GucluBirSifreYazin"
```

Komut şifreyi `KARGO_ADMIN_PASSWORD` ortam değişkeninden okuyabilir:

```bash
python manage.py admin_hazirla
```

Panel girişi:

```text
/panel/giris/
```
