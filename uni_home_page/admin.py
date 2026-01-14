# Django admin paneliyle ilgili araçları (ModelAdmin, register vb.) kullanmak için import eder
from django.contrib import admin

# Bu app içindeki modelleri import eder (admin panelinde yönetebilmek için)
from .models import University, Post, PostLike, PostComment, PostView


# Post modelini admin paneline "decorator" ile kaydeder
# Böylece Post için özelleştirilmiş PostAdmin ayarları uygulanır
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Admin listesinde (Post liste ekranında) hangi kolonlar gözüksün
    list_display = ("id", "title", "category", "author", "is_approved", "created_at")

    # Sağ tarafta filtre panelinde hangi alanlara göre filtreleme yapılabilsin
    list_filter = ("category", "is_approved", "created_at")

    # Üstteki arama kutusunun hangi alanlarda arama yapacağını belirler
    # author__username ile ilişki üzerinden yazarın username'i içinde de arama yapar
    search_fields = ("title", "content", "author__username")

    # Liste ekranında direkt düzenlenebilir alanlar (detay sayfasına girmeden)
    # Burada onay durumunu listeden hızlıca değiştirebilirsin
    list_editable = ("is_approved",)


# University modelini admin paneline default ayarlarla kaydeder
admin.site.register(University)

# PostLike modelini admin paneline default ayarlarla kaydeder (beğeni kayıtları)
admin.site.register(PostLike)

# PostComment modelini admin paneline default ayarlarla kaydeder (yorum kayıtları)
admin.site.register(PostComment)

# PostView modelini admin paneline default ayarlarla kaydeder (görüntülenme kayıtları)
admin.site.register(PostView)
