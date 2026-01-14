# Django URL routing sistemi için path fonksiyonunu import eder
from django.urls import path

# Aynı klasördeki views.py dosyasını import eder
from . import views


# Uygulamaya ait tüm URL yönlendirmeleri burada tanımlanır
urlpatterns = [

    # =========================
    # ANA SAYFA
    # =========================

    # Ana sayfa ("/")
    path('', views.home, name='home'),


    # =========================
    # AUTH (GİRİŞ / KAYIT / ÇIKIŞ)
    # =========================

    # Kullanıcı giriş sayfası
    path("login/", views.login_page, name='login'),

    # Kullanıcı kayıt sayfası
    path("register/", views.register_page, name='register'),

    # Kullanıcı çıkış (logout) işlemi
    path("logout/", views.logout_user, name='logout'),


    # =========================
    # KATEGORİ SAYFALARI
    # =========================

    # Gündem haberleri listesi
    path("gundem/", views.gundem, name='gundem'),

    # Etkinlikler kategorisi
    path("etkinlikler/", views.etkinlikler, name='etkinlikler'),

    # Duyurular kategorisi
    path("duyurular/", views.duyurular, name='duyurular'),

    # Kulüp & topluluk haberleri
    path("kulup/", views.kulup, name="kulup"),


    # =========================
    # ŞİFRE SIFIRLAMA
    # =========================

    # Şifre sıfırlama isteği sayfası
    path("password_reset/", views.password_reset_request, name="password_reset"),


    # =========================
    # ADMİN PANELİ (CUSTOM)
    # =========================

    # Custom admin dashboard ana sayfası
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Admin post düzenleme (⚠️ altta detaylı edit route da var)
    path("admin_edit_post/", views.admin_edit_post, name="admin_edit_post"),


    # =========================
    # POST DETAY & ETKİLEŞİM
    # =========================

    # Post detay sayfası (pk = post id)
    path("post/<int:pk>/", views.post_detail, name="post_detail"),

    # Post beğen / beğeniyi kaldır (toggle)
    path("post/<int:pk>/like/", views.toggle_like, name="toggle_like"),

    # Posta yorum ekleme
    path("post/<int:pk>/comment/", views.add_comment, name="add_comment"),


    # =========================
    # ADMİN POST İŞLEMLERİ
    # =========================

    # Admin: post onaylama
    path(
        "admin_dashboard/post/<int:pk>/approve/",
        views.admin_approve_post,
        name="admin_approve_post"
    ),

    # Admin: post reddetme
    path(
        "admin_dashboard/post/<int:pk>/reject/",
        views.admin_reject_post,
        name="admin_reject_post"
    ),

    # Admin: post silme (soft delete olabilir)
    path(
        "admin_dashboard/post/<int:pk>/delete/",
        views.admin_delete_post,
        name="admin_delete_post"
    ),

    # Admin: silinen postu geri alma
    path(
        "admin_dashboard/post/<int:pk>/restore/",
        views.admin_restore_post,
        name="admin_restore_post"
    ),

    # Admin: post düzenleme (ID ile)
    path(
        "admin_dashboard/post/<int:pk>/edit/",
        views.admin_edit_post,
        name="admin_edit_post"
    ),


    # =========================
    # KULÜP YETKİLİSİ POST DÜZENLEME
    # =========================

    # Kulüp yetkilisinin kendi postunu düzenlemesi
    path(
        "club/post/<int:pk>/edit/",
        views.club_edit_own_post,
        name="club_edit_own_post"
    ),


    # =========================
    # POST OLUŞTURMA
    # =========================

    # Yeni post / haber gönderme sayfası
    path("submit-post/", views.submit_post, name="submit_post"),


    # =========================
    # ADMİN TOPLU İŞLEMLER
    # =========================

    # Admin panelinden toplu post işlemleri (onay/red/sil vb.)
    path(
        "admin_dashboard/bulk-action/",
        views.admin_bulk_action,
        name="admin_bulk_action"
    ),


    # =========================
    # ADMİN KULLANICI ROL YÖNETİMİ
    # =========================

    # Admin: kullanıcı rollerini listeleme
    path(
        "admin_dashboard/users/",
        views.admin_user_roles,
        name="admin_user_roles"
    ),

    # Admin: tek bir kullanıcının rolünü değiştirme
    path(
        "admin_dashboard/users/<int:user_id>/role/",
        views.admin_set_user_role,
        name="admin_set_user_role"
    ),

    # ⚠️ Yukarıdakiyle benzer: kullanıcı rollerini user_id ile çağırma
    path(
        "admin_dashboard/user/<int:user_id>/roles/",
        views.admin_user_roles,
        name="admin_user_roles"
    ),


    # =========================
    # API ENDPOINT
    # =========================

    # Üniversite seçimine göre bölümleri dönen API
    path(
        "api/departments/",
        views.api_departments,
        name="api_departments"
    ),


    # =========================
    # AI İŞLEMLERİ
    # =========================

    # UniNews AI sohbet geçmişini temizleme
    path(
        "ai/clear/",
        views.clear_ai_history,
        name="clear_ai_history"
    ),
]
