# Django ayarlarını (AUTH_USER_MODEL gibi) kullanmak için import edilir
from django.conf import settings

# Django ORM (Object Relational Mapper) için gerekli model sınıfları
from django.db import models

# Zamanla ilgili işlemler için Django'nun timezone modülü
from django.utils import timezone

# Üniversite modeli başka bir app'ten import ediliyor
# Bu projede TEK bir University modeli kullanıldığını belirtir
from uni_home_page.models import University  # ✅ TEK University modeli burada


# Üniversiteye bağlı bölümleri temsil eden model
class Department(models.Model):

    # Bölümün bağlı olduğu üniversite (ForeignKey ilişki)
    university = models.ForeignKey(
        University,                 # İlişkili model
        on_delete=models.CASCADE,   # Üniversite silinirse bölümler de silinir
        related_name="departments"  # university.departments.all() ile erişim
    )

    # Bölüm adı alanı (örneğin: Bilgisayar Mühendisliği)
    name = models.CharField(
        max_length=150              # Maksimum 150 karakter
    )

    class Meta:
        # Aynı üniversite altında aynı isimde bir bölüm tekrar eklenemesin diye
        # bileşik (compound) benzersizlik kuralı
        unique_together = ("university", "name")

        # Bölümler varsayılan olarak isme göre alfabetik sıralansın
        ordering = ["name"]

    def __str__(self):
        # Admin paneli ve shell'de okunabilir string gösterimi
        # Örn: "Boğaziçi Üniversitesi - Bilgisayar Mühendisliği"
        return f"{self.university.name} - {self.name}"


# Kullanıcı profiline ait bilgileri tutan model
class Profile(models.Model):

    # Django'nun kullanıcı modeli ile bire bir ilişki (OneToOne)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,   # Custom User varsa uyumlu çalışır
        on_delete=models.CASCADE,   # Kullanıcı silinirse profil de silinir
        related_name="profile"      # user.profile ile erişim sağlar
    )

    # Kullanıcının üniversitesi (opsiyonel)
    university = models.ForeignKey(
        University,                 # İlişkili üniversite modeli
        on_delete=models.SET_NULL,  # Üniversite silinirse profil silinmez
        null=True,                  # Veritabanında NULL olabilir
        blank=True,                 # Formlarda boş bırakılabilir
        related_name="profiles"     # reverse ilişki çakışmasını önler
    )

    # Kullanıcının bölümü (opsiyonel)
    department = models.ForeignKey(
        Department,                # İlişkili bölüm modeli
        on_delete=models.SET_NULL, # Bölüm silinirse profil silinmez
        null=True,                 # Veritabanında NULL olabilir
        blank=True,                # Formlarda boş bırakılabilir
        related_name="profiles"    # department.profiles.all()
    )

    # Kullanıcının profil fotoğrafı
    avatar = models.ImageField(
        upload_to="avatars/",      # MEDIA_ROOT/avatars/ dizinine kaydedilir
        null=True,
        blank=True
    )

    # Kullanıcının bildirim ayarını tutar
    notifications_enabled = models.BooleanField(
        default=True               # Varsayılan olarak bildirimler açık
    )

    # Profilin oluşturulma tarihi
    created_at = models.DateTimeField(
        default=timezone.now       # Kayıt anındaki zamanı otomatik alır
    )

    def __str__(self):
        # Profil nesnesi string'e çevrildiğinde kullanıcıyı gösterir
        return str(self.user)
