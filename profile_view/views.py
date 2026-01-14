# Kullanıcının giriş yapmış olmasını zorunlu kılan decorator
from django.contrib.auth.decorators import login_required

# Template render etmek ve yönlendirme yapmak için
from django.shortcuts import render, redirect

# Yetkisiz erişimler için HTTP 403 cevabı döndürmek için
from django.http import HttpResponseForbidden

# Django mesaj (flash message) sistemi
from django.contrib import messages

# Profile modeli
from .models import Profile

# Profil düzenleme formu
from .forms import ProfileForm

# Ana uygulamadaki gönderi (post) ile ilgili modeller
from uni_home_page.models import Post, PostLike, PostComment, PostView

# Haber / gönderi oluşturma formu
from uni_home_page.forms import PostSubmitForm


# -------------------------------
# PROFİL GÖRÜNTÜLEME SAYFASI
# -------------------------------
@login_required
def profile_view_page(request):
    # Kullanıcıya ait profil yoksa oluştur, varsa getir
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Kullanıcının yaptığı toplam beğeni sayısı
    like_count = PostLike.objects.filter(user=request.user).count()

    # Kullanıcının yaptığı toplam yorum sayısı
    comment_count = PostComment.objects.filter(user=request.user).count()

    # Kullanıcının yazdığı etkinlik kategorisindeki gönderi sayısı
    event_count = Post.objects.filter(
        author=request.user,
        category=Post.Category.ETKINLIK
    ).count()

    # Kullanıcının beğendiği, onaylanmış gönderiler (en fazla 8 adet)
    liked_posts = (
        Post.objects.filter(
            likes__user=request.user,   # Kullanıcının beğendiği postlar
            is_approved=True            # Admin onaylı olanlar
        )
        .select_related("author")      # Author için ek sorgu atılmasın
        .distinct()                    # Aynı post tekrar etmesin
        [:8]                           # Limit
    )

    # Kullanıcının son görüntülediği gönderileri kategoriye göre getiren yardımcı fonksiyon
    def recent_by(cat):
        return (
            Post.objects.filter(
                views__user=request.user,  # Kullanıcının görüntülediği postlar
                category=cat,               # Kategori filtresi
                is_approved=True,           # Onaylı gönderiler
            )
            .order_by("-views__last_viewed_at")  # En son bakılan en üstte
            .distinct()
            [:5]                                # Her kategori için 5 adet
        )

    # Kategorilere göre son görüntülenen gönderiler
    recent_gundem = recent_by(Post.Category.GUNDEM)
    recent_etkinlik = recent_by(Post.Category.ETKINLIK)
    recent_duyuru = recent_by(Post.Category.DUYURU)
    recent_kulup = recent_by(Post.Category.KULUP)

    # Kullanıcının admin onayında bekleyen gönderileri
    my_pending_posts = (
        Post.objects.filter(
            author=request.user,
            is_approved=False
        )
        .order_by("-id")[:8]
    )

    # Kullanıcının yayınlanmış gönderileri
    my_published_posts = (
        Post.objects.filter(
            author=request.user,
            is_approved=True
        )
        .order_by("-id")[:8]
    )

    # Profil sayfasındaki mini haber gönderme formu
    post_form = PostSubmitForm()

    # Eğer POST isteği geldiyse ve bu istek haber gönderme amacı taşıyorsa
    if request.method == "POST" and request.POST.get("_action") == "submit_post":

        # Admin kullanıcılar profilden haber gönderemesin
        if request.user.is_staff:
            return HttpResponseForbidden("Adminler profilden haber gönderemez.")

        # Formu POST verileri ve dosyalarla doldur
        post_form = PostSubmitForm(request.POST, request.FILES)

        # Form geçerliyse
        if post_form.is_valid():
            post = post_form.save(commit=False)  # Veritabanına hemen kaydetme
            post.author = request.user           # Yazarı mevcut kullanıcı yap
            post.is_approved = False             # Admin onayı beklesin
            post.save()

            # Kullanıcıya başarı mesajı göster
            messages.success(
                request,
                "Haberin gönderildi ✅ Admin onayından sonra yayınlanacak."
            )

            # Profil sayfasına geri yönlendir
            return redirect("profile_view")

        else:
            # Form hatalıysa hata mesajı göster
            messages.error(
                request,
                "Haber gönderilemedi ❌ Lütfen alanları kontrol et."
            )

    # Template'e gönderilecek veriler
    context = {
        "profile": profile,
        "like_count": like_count,
        "comment_count": comment_count,
        "event_count": event_count,
        "liked_posts": liked_posts,
        "recent_gundem": recent_gundem,
        "recent_etkinlik": recent_etkinlik,
        "recent_duyuru": recent_duyuru,
        "recent_kulup": recent_kulup,
        "post_form": post_form,

        # Kullanıcının gönderileri
        "my_pending_posts": my_pending_posts,
        "my_published_posts": my_published_posts,
    }

    # Profil sayfasını render et
    return render(request, "profile_view.html", context)


# -------------------------------
# PROFİL DÜZENLEME SAYFASI
# -------------------------------
@login_required
def edit_profile(request):
    # Kullanıcının profili yoksa oluştur
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Eğer form POST edildiyse
    if request.method == "POST":
        # Mevcut profil instance'ı ile formu doldur
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        # Form geçerliyse
        if form.is_valid():
            form.save()  # Profili güncelle
            messages.success(request, "Profil güncellendi ✅")
            return redirect("profile_view")
        else:
            messages.error(
                request,
                "Profil güncellenemedi ❌ Lütfen alanları kontrol et."
            )

    else:
        # GET isteğinde mevcut profil bilgileriyle formu doldur
        form = ProfileForm(instance=profile)

    # Profil düzenleme sayfasını render et
    return render(
        request,
        "edit_profile.html",
        {
            "form": form,
            "profile": profile
        }
    )
