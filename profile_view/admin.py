# Django'nun admin paneliyle ilgili araçlarını içe aktarır
from django.contrib import admin

# Aynı uygulama (app) içindeki Profile ve Department modellerini içe aktarır
from .models import Profile, Department


# Profile modelini Django admin paneline kaydeder
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Admin panelinde Profile kayıtları listelenirken gösterilecek alanlar
    list_display = (
        "user",                    # Profili oluşturan kullanıcı
        "university",              # Kullanıcının üniversitesi
        "department",              # Kullanıcının bölümü
        "notifications_enabled",   # Bildirimlerin açık/kapalı durumu
        "created_at"               # Profilin oluşturulma tarihi
    )

    # Admin panelinde arama yapılabilecek alanlar
    # "__" kullanımı ilişkili modellere erişim sağlar (ForeignKey)
    search_fields = (
        "user__username",          # Kullanıcı adı üzerinden arama
        "user__email",             # Kullanıcının e-postası üzerinden arama
        "university__name",        # Üniversite adı üzerinden arama
        "department__name"         # Bölüm adı üzerinden arama
    )

    # Sağ tarafta filtreleme yapılabilecek alanlar
    list_filter = (
        "notifications_enabled",   # Bildirim durumu filtreleme
        "university"               # Üniversiteye göre filtreleme
    )


# Department modelini Django admin paneline kaydeder
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    # Admin panelinde Department kayıtları listelenirken gösterilecek alanlar
    list_display = (
        "name",        # Bölüm adı
        "university"   # Bölümün bağlı olduğu üniversite
    )

    # Bölümler için admin panelinde arama yapılabilecek alanlar
    search_fields = (
        "name",              # Bölüm adına göre arama
        "university__name"   # Üniversite adına göre arama
    )

    # Üniversiteye göre filtreleme yapılmasını sağlar
    list_filter = (
        "university",        # Üniversite filtresi
    )
