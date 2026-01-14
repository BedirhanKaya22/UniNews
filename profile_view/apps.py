# Django uygulamalarını yapılandırmak için kullanılan AppConfig sınıfını içe aktarır
from django.apps import AppConfig


# profile_view uygulaması için özel yapılandırma sınıfı
class ProfileViewConfig(AppConfig):
    # Otomatik oluşturulan primary key alanlarının varsayılan tipini belirler
    # BigAutoField = 64-bit integer (büyük projeler için uygundur)
    default_auto_field = "django.db.models.BigAutoField"

    # Bu AppConfig'in ait olduğu Django uygulamasının adı
    # settings.py içindeki INSTALLED_APPS ile aynı olmalıdır
    name = "profile_view"

    def ready(self):
        """
        Django uygulaması tamamen yüklendikten sonra çalışır.
        Genellikle signal (post_save, pre_save vb.) tanımlamalarını
        güvenli şekilde import etmek için kullanılır.
        """

        # signals.py dosyasını import eder
        # Bu sayede signal'lar uygulama başlarken otomatik olarak register edilir
        from . import signals  # noqa
        # noqa: Linter (flake8 vb.) uyarı vermesin diye eklenir
        # (import kullanıldı ama değişken olarak kullanılmadı uyarısı)
