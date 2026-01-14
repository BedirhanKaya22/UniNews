# Django ayarlarına (settings.py) erişmek için kullanılır
from django.conf import settings

# Django ORM (Model, Field vs.) kullanabilmek için import edilir
from django.db import models

# Metni URL-uyumlu slug'a çevirmek için kullanılır
from django.utils.text import slugify


# Projede kullanılan User modelini dinamik olarak alır
# (Custom user varsa otomatik uyum sağlar)
User = settings.AUTH_USER_MODEL


# =========================
# ÜNİVERSİTE MODELİ
# =========================
class University(models.Model):
    # Üniversitenin adı (benzersiz olmalı)
    name = models.CharField(max_length=200, unique=True)

    # Üniversite için URL-dostu slug alanı
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        # Üniversiteler alfabetik sırayla listelensin
        ordering = ["name"]

    def save(self, *args, **kwargs):
        """
        Model kaydedilmeden önce slug boşsa
        otomatik olarak üniversite adından slug üretir
        """
        if not self.slug:
            # slugify ile URL-uyumlu hale getirip max uzunluğa keser
            self.slug = slugify(self.name)[:220]

        # Asıl kaydetme işlemi
        super().save(*args, **kwargs)

    def __str__(self):
        # Admin panelinde ve shell'de görünen temsil
        return self.name


# =========================
# POST / HABER MODELİ
# =========================
class Post(models.Model):

    # ---------
    # KATEGORİLER
    # ---------
    class Category(models.TextChoices):
        GUNDEM = "GUNDEM", "Gündem"
        ETKINLIK = "ETKINLIK", "Etkinlikler"
        DUYURU = "DUYURU", "Duyurular"
        KULUP = "KULUP", "Kulüpler & Topluluklar"

    # ---------
    # DURUM (ONAY SÜRECİ)
    # ---------
    class Status(models.TextChoices):
        PENDING = "PENDING", "Onay Bekliyor"
        APPROVED = "APPROVED", "Onaylandı"
        REJECTED = "REJECTED", "Reddedildi"

    # Postun onay durumu (admin workflow)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,  # Sorgularda hız kazandırır
    )

    # Postu oluşturan kullanıcı
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    # Haber başlığı
    title = models.CharField(max_length=200)

    # Kısa özet (opsiyonel)
    summary = models.CharField(max_length=300, blank=True, null=True)

    # Haber içeriği (uzun metin)
    content = models.TextField()

    # Haber kategorisi
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GUNDEM
    )

    # Kapak görseli (opsiyonel)
    cover = models.ImageField(
        upload_to="post_covers/",
        blank=True,
        null=True
    )

    # Eski bir onay alanı (status ile birlikte kullanılabilir)
    is_approved = models.BooleanField(default=False)

    # Oluşturulma tarihi (ilk kayıtta otomatik)
    created_at = models.DateTimeField(auto_now_add=True)

    # Güncellenme tarihi (her save'de otomatik)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # En yeni postlar üstte görünsün
        ordering = ["-created_at"]

    def __str__(self):
        # Admin paneli için okunabilir temsil
        return self.title


# =========================
# POST BEĞENİ MODELİ
# =========================
class PostLike(models.Model):
    # Beğeniyi yapan kullanıcı
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )

    # Beğenilen post
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    # Beğeninin oluşturulma tarihi
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Aynı kullanıcı aynı postu sadece 1 kez beğenebilir
        unique_together = ("user", "post")

        # En yeni beğeniler üstte
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.post}"


# =========================
# POST YORUM MODELİ
# =========================
class PostComment(models.Model):
    # Yorumu yazan kullanıcı
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_comments"
    )

    # Yorum yapılan post
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    # Yorum metni
    text = models.TextField(max_length=1500)

    # Yorum tarihi
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # En yeni yorumlar üstte
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.post}"


# =========================
# POST GÖRÜNTÜLENME MODELİ
# =========================
class PostView(models.Model):
    # Postu görüntüleyen kullanıcı
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_views"
    )

    # Görüntülenen post
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="views"
    )

    # Son görüntülenme zamanı (her view'de güncellenir)
    last_viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Aynı kullanıcı aynı post için tek kayıt
        unique_together = ("user", "post")

        # En son görüntülenenler üstte
        ordering = ["-last_viewed_at"]

    def __str__(self):
        return f"{self.user} saw {self.post}"


# =========================
# AI SORU / CEVAP MODELİ
# =========================
class AIMessage(models.Model):
    # Soruyu soran kullanıcı (anonim olabilir)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_messages",
        null=True,
        blank=True,
    )

    # Kullanıcının AI'ya sorduğu soru
    question = models.TextField()

    # AI tarafından üretilen cevap
    answer = models.TextField()

    # Oluşturulma zamanı
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # En yeni AI mesajları üstte
        ordering = ["-created_at"]

    def __str__(self):
        # Kullanıcı varsa id, yoksa anon göster
        return f"{self.user_id or 'anon'} - {self.created_at:%Y-%m-%d %H:%M}"
