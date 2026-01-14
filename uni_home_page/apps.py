# Django uygulamalarının yapılandırmasını yapmak için kullanılan temel sınıf
from django.apps import AppConfig


# Bu sınıf, uni_home_page uygulamasının Django'ya nasıl tanıtılacağını belirler
class UniHomePageConfig(AppConfig):

    # Model'lerde varsayılan olarak kullanılacak primary key (id) alanının tipi
    # BigAutoField: büyük projelerde id sınırına takılmamak için tercih edilir
    default_auto_field = "django.db.models.BigAutoField"

    # Django'ya uygulamanın python path'ini söyler
    # settings.py içindeki INSTALLED_APPS'te bu isim kullanılır
    name = "uni_home_page"
