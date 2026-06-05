from django.urls import path

from . import views

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('firma/<slug:slug>/', views.sirket_detay, name='sirket_detay'),
    path('sirket/<int:pk>/', views.eski_sirket_detay, name='eski_sirket_detay'),
    path('panel/giris/', views.panel_giris, name='panel_giris'),
    path('panel/cikis/', views.panel_cikis, name='panel_cikis'),
    path('panel/', views.panel, name='panel'),
    path('panel/sirket/yeni/', views.sirket_form, name='sirket_yeni'),
    path('panel/sirket/<int:pk>/', views.sirket_detay_panel, name='panel_sirket_detay'),
    path('panel/sirket/<int:pk>/duzenle/', views.sirket_form, name='sirket_duzenle'),
    path('panel/sirket/<int:pk>/yayinla/', views.sirket_yayinla, name='sirket_yayinla'),
    path('panel/sirket/<int:pk>/yayindan-kaldir/', views.sirket_yayindan_kaldir, name='sirket_yayindan_kaldir'),
    path('panel/sirket/<int:pk>/sil/', views.sirket_sil, name='sirket_sil'),
    path('panel/sirket/<int:sirket_pk>/urun/yeni/', views.urun_form, name='urun_yeni'),
    path('panel/urun/<int:pk>/duzenle/', views.urun_form, name='urun_duzenle'),
    path('panel/urun/<int:pk>/sil/', views.urun_sil, name='urun_sil'),
]
