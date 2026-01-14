# Django'nun URL yönlendirme sistemi için path fonksiyonunu içe aktarır
from django.urls import path

# Aynı uygulama (app) içindeki views.py dosyasını içe aktarır
from . import views


# Bu uygulamaya ait URL tanımlarının listesi
urlpatterns = [

    # /profile_view/ adresine gelen istekleri
    # views.py içindeki profile_view_page fonksiyonuna yönlendirir
    path(
        "profile_view/",            # URL yolu
        views.profile_view_page,    # Çalıştırılacak view fonksiyonu
        name="profile_view"         # URL'yi template'lerde kullanmak için isim
    ),

    # /profil/duzenle/ adresine gelen istekleri
    # views.py içindeki edit_profile fonksiyonuna yönlendirir
    path(
        "profil/duzenle/",          # URL yolu (Türkçe slug)
        views.edit_profile,         # Profil düzenleme view'i
        name="edit_profile"         # reverse() ve {% url %} için isim
    ),
]
