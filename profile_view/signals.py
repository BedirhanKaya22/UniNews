# Projedeki aktif User modelini (default ya da custom) almak için kullanılır
from django.contrib.auth import get_user_model

# Django sinyal sistemi: bir model kaydedildikten sonra tetiklenir
from django.db.models.signals import post_save

# Sinyalleri fonksiyonlara bağlamak için kullanılan decorator
from django.dispatch import receiver

# Aynı uygulama içindeki Profile modelini içe aktarır
from .models import Profile


# Projede kullanılan User modelini değişkene atar
# Custom User kullanılsa bile otomatik uyum sağlar
User = get_user_model()


# User modeli her kaydedildiğinde (save) çalışacak signal
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Yeni bir kullanıcı oluşturulduğunda otomatik olarak
    o kullanıcıya ait bir Profile nesnesi oluşturur.
    """

    # Eğer bu save işlemi yeni bir kullanıcı oluşturma işlemi ise
    if created:
        # Aynı kullanıcı için birden fazla profil oluşmasını engellemek için
        # get_or_create kullanılır
        Profile.objects.get_or_create(
            user=instance  # Profilin bağlanacağı kullanıcı
        )
