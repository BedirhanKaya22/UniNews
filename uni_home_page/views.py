# AUTO-YORUMLU SÜRÜM – ORİJİNAL DOSYA KESİLMEDEN KORUNMUŞTUR
# Sadece açıklayıcı Python yorumları eklenmiştir.

# Django shortcut'ları: render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
# Django auth: kullanıcı giriş/çıkış işlemleri
from django.contrib.auth import authenticate, login, logout
# Pagination (sayfalama) sistemi
from django.core.paginator import Paginator
# Q ve Count: gelişmiş ORM sorguları
from django.db.models import Q  , Count
from django.contrib.auth.models import User
from django.contrib import messages
# staff_member_required: sadece admin/staff erişimi
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.conf import settings

from gundem import models
from .forms import RegisterForm
# Google Gemini AI entegrasyonu
import google.generativeai as genai
from .forms import PostSubmitForm, ProfileUpdateForm
from .models import Post, PostLike, PostComment, PostView
from .models import AIMessage
from .forms import uninewsaiform
from profile_view.models import Department, University, Profile

# ----------------------
# BASIC PAGES
# ----------------------
# Ana sayfa: login olmayanlar düz sayfa, login olanlar AI paneli görür
def home(request):
    # Login değilse sadece sayfayı göster
    if not request.user.is_authenticated:
        return render(request, "home.html")

    # Login ise AI formu + geçmiş
    form = uninewsaiform(request.POST or None)

    if request.method == "POST" and form.is_valid():
        question = form.cleaned_data["question"]

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(question)
        answer = response.text

        AIMessage.objects.create(
            user=request.user,
            question=question,
            answer=answer
        )

        return redirect("home")  # post tekrarını önler

    history = AIMessage.objects.filter(user=request.user)[:30]

    return render(request, "home.html", {
        "form": form,
        "history": history
    })


def gundem(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED, category=Post.Category.GUNDEM).order_by("-created_at")
    return render(request, "gundem.html", {"posts": posts})

def etkinlikler(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED, category=Post.Category.ETKINLIK).order_by("-created_at")
    return render(request, "etkinlikler.html", {"posts": posts})

def duyurular(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED, category=Post.Category.DUYURU).order_by("-created_at")
    return render(request, "duyurular.html", {"posts": posts})

def kulup(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED, category=Post.Category.KULUP).order_by("-created_at")
    return render(request, "kulup_ve_topluluklar.html", {"posts": posts})



def password_reset_request(request):
    return render(request, "password_reset.html")


# ----------------------
# AUTH
# ----------------------
# Kullanıcı kayıt + profil/üniversite/bölüm oluşturma
def register_page(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password1 = form.cleaned_data["password1"]

            # Text inputlardan gelecek (senin yeni template’ine göre)
            uni_name = (form.cleaned_data.get("university_name") or "").strip()
            dep_name = (form.cleaned_data.get("department_name") or "").strip()

            if User.objects.filter(username=username).exists():
                messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
                return render(request, "register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "Bu e-posta zaten kayıtlı.")
                return render(request, "register.html", {"form": form})

            user = User.objects.create_user(username=username, email=email, password=password1)

            # Profile garanti olsun (signal yoksa patlamasın)
            profile, _ = Profile.objects.get_or_create(user=user)

            # Üniversite/Bölüm DB’ye yaz
            uni, _ = University.objects.get_or_create(name=uni_name)
            dep, _ = Department.objects.get_or_create(university=uni, name=dep_name)

            profile.university = uni
            profile.department = dep
            profile.save()

            messages.success(request, "Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_page(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Hatalı giriş.")

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    return redirect("home")


# ----------------------
# HELPERS
# ----------------------
def is_club_admin(user):
    return user.is_authenticated and user.groups.filter(name="club_admin").exists()

def is_approved_publisher(user):
    return user.groups.filter(name="approved_publisher").exists()


# ----------------------
# ADMIN DASHBOARD
# ----------------------

@staff_member_required
# Admin dashboard: filtreleme, pagination ve istatistikler
def admin_dashboard(request):
    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip().upper()
    status = (request.GET.get("status") or "").strip().upper()
    sort = (request.GET.get("sort") or "new").strip().lower()

    # 1️⃣ ANA QUERYSET
    posts_qs = Post.objects.select_related("author").all()

    if q:
        posts_qs = posts_qs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(author__username__icontains=q)
        )

    if category in dict(Post.Category.choices):
        posts_qs = posts_qs.filter(category=category)

    if status in dict(Post.Status.choices):
        posts_qs = posts_qs.filter(status=status)

    if sort == "old":
        posts_qs = posts_qs.order_by("created_at")
    else:
        posts_qs = posts_qs.order_by("-created_at")

    # 2️⃣ DURUMA GÖRE AYIR
    approved_items = posts_qs.filter(status=Post.Status.APPROVED)
    pending_items  = posts_qs.filter(status=Post.Status.PENDING)
    rejected_items = posts_qs.filter(status=Post.Status.REJECTED)

    # 🟢 EKLENDİ: PAGINATION (TAM BURAYA)
    approved_paginator = Paginator(approved_items, 10)
    page_number = request.GET.get("page")
    approved_page = approved_paginator.get_page(page_number)

    # 3️⃣ İSTATİSTİKLER
    stats = {
        "total_news": Post.objects.filter(category=Post.Category.GUNDEM, status=Post.Status.APPROVED).count(),
        "total_events": Post.objects.filter(category=Post.Category.ETKINLIK, status=Post.Status.APPROVED).count(),
        "total_announcements": Post.objects.filter(category=Post.Category.DUYURU, status=Post.Status.APPROVED).count(),
        "total_clubs": Post.objects.filter(category=Post.Category.KULUP, status=Post.Status.APPROVED).count(),
        "total_users": User.objects.count(),
        "total_comments": PostComment.objects.count(),
        "total_likes": PostLike.objects.count(),
        "pending_approvals": Post.objects.filter(status=Post.Status.PENDING).count(),
    }

    latest_news = Post.objects.filter(status=Post.Status.APPROVED).order_by("-created_at")[:10]
    latest_comments = PostComment.objects.order_by("-created_at")[:10]
    latest_users = User.objects.order_by("-date_joined")[:10]

    # 🟢 EKLENDİ: approved_page BURADA RETURN EDİLİR
    return render(request, "admin_dashboard.html", {
        "stats": stats,

        "approved_items": approved_items,
        "pending_items": pending_items,
        "rejected_items": rejected_items,

        "approved_page": approved_page,  # 👈 HTML bunu kullanıyor

        "latest_news": latest_news,
        "latest_comments": latest_comments,
        "latest_users": latest_users,

        "q": q,
        "category": category,
        "status": status,
        "sort": sort,
    })

@staff_member_required
@require_POST
# Admin toplu işlemler (approve/delete)
def admin_bulk_action(request):
    action = request.POST.get("action")
    post_ids = request.POST.getlist("post_ids")

    if not post_ids:
        messages.warning(request, "Hiç içerik seçilmedi.")
        return redirect("admin_dashboard")

    posts = Post.objects.filter(id__in=post_ids)

    if action == "approve":
        posts.update(
            status=Post.Status.APPROVED,
            is_approved=True
        )
        messages.success(request, f"{posts.count()} içerik onaylandı.")

    elif action == "delete":
        count = posts.count()
        posts.delete()
        messages.warning(request, f"{count} içerik silindi.")

    else:
        messages.error(request, "Geçersiz işlem.")

    return redirect("admin_dashboard")



# ----------------------
# POST ACTIONS (SUBMIT + ADMIN)
# ----------------------
@login_required
# İçerik gönderimi + otomatik onay kontrolü
def submit_post(request):
    if request.method != "POST":
        return redirect("home")

    category = request.POST.get("category")

    # Kulüp yetkisi kontrolü (kulüp postu sadece staff veya club_admin)
    if category == Post.Category.KULUP and not (request.user.is_staff or is_club_admin(request.user)):
        messages.error(request, "Kulüp içeriği göndermek için yetkin yok.")
        return redirect("admin_dashboard")

    form = PostSubmitForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Form hatalı. Alanları kontrol et.")
        return redirect("admin_dashboard")

    post = form.save(commit=False)
    post.author = request.user

    auto_approve = False
    if request.user.is_staff:
        auto_approve = True
    if is_approved_publisher(request.user):
        auto_approve = True
    if is_club_admin(request.user) and category == Post.Category.KULUP:
        auto_approve = True

    if auto_approve:
        post.status = Post.Status.APPROVED
        post.is_approved = True
        messages.success(request, "İçerik yayınlandı (otomatik onay).")
    else:
        post.status = Post.Status.PENDING
        post.is_approved = False
        messages.success(request, "İçerik gönderildi. Onay bekliyor.")

    post.save()
    return redirect("admin_dashboard")



@staff_member_required
def admin_approve_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = Post.Status.APPROVED
    post.is_approved = True
    post.save(update_fields=["status", "is_approved", "updated_at"])
    messages.success(request, "İçerik onaylandı.")
    return redirect("admin_dashboard")




@staff_member_required
def admin_reject_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = Post.Status.REJECTED
    post.is_approved = False
    post.save(update_fields=["status", "is_approved", "updated_at"])
    messages.warning(request, "İçerik reddedildi (arşivlendi).")
    return redirect("admin_dashboard")



@staff_member_required
def admin_delete_post(request, pk):
    # ❗ Bu gerçek silme (istersen soft delete yaparız ama şimdilik hard delete)
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.warning(request, "İçerik silindi.")
    return redirect("admin_dashboard")


@staff_member_required
def admin_restore_post(request, pk):
    # ✅ Reddedileni geri al → tekrar PENDING
    post = get_object_or_404(Post, pk=pk)
    post.status = Post.Status.PENDING
    post.is_approved = False
    post.save(update_fields=["status", "is_approved", "updated_at"])
    messages.success(request, "İçerik geri alındı (onay bekliyor).")
    return redirect("admin_dashboard")


@staff_member_required
def admin_edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostSubmitForm(instance=post)

    if request.method == "POST":
        form = PostSubmitForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "İçerik güncellendi.")
            return redirect("admin_dashboard")
        messages.error(request, "Form hatalı. Lütfen alanları kontrol et.")

    return render(request, "admin_edit_post.html", {"form": form, "post": post})



@login_required
def club_edit_own_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if not request.user.is_staff:
        if not is_club_admin(request.user) or post.author_id != request.user.id:
            return HttpResponseForbidden("Bu içeriği düzenleme yetkin yok.")

    form = PostSubmitForm(instance=post)

    if request.method == "POST":
        form = PostSubmitForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "İçerik güncellendi.")
            return redirect("admin_dashboard")
        messages.error(request, "Form hatalı. Lütfen alanları kontrol et.")

    return render(request, "admin_edit_post.html", {"form": form, "post": post})


@staff_member_required
# Kullanıcı rol yönetimi ve istatistik hesaplama
def admin_user_roles(request):
    """
    Kullanıcı listesi + istatistikler (senin admin panelinin içinde render edeceğiz)
    """
    # Roller (Group) – senin kullanacağın rol isimleri
    role_groups = Group.objects.filter(name__in=["approved_publisher", "club_admin"])

    # Kullanıcı istatistikleri:
    # posts: Post modelinde author FK var => related_name="posts"
    # likes/comments/views: PostLike/PostComment/PostView post->author üzerinden sayılıyor
    users = (
        User.objects.all()
        .annotate(
            post_count=Coalesce(Count("posts", distinct=True), 0),
            total_likes_received=Coalesce(Count("posts__likes", distinct=True), 0),
            total_comments_received=Coalesce(Count("posts__comments", distinct=True), 0),
            total_views_received=Coalesce(Count("posts__views", distinct=True), 0),
        )
        .order_by("-date_joined")
    )

    # Arama (opsiyonel)
    q = (request.GET.get("q") or "").strip()
    if q:
        users = users.filter(username__icontains=q)

    # Rol etiketi hesapla (template’de kolay göstermek için)
    for u in users:
        if u.is_superuser:
            u.role_label = "superadmin"
        elif u.is_staff:
            u.role_label = "admin"
        elif u.groups.filter(name="approved_publisher").exists():
            u.role_label = "onaylı yayıncı"
        elif u.groups.filter(name="club_admin").exists():
            u.role_label = "kulüp admin"
        else:
            u.role_label = "user"


    return render(request, "admin_user_roles.html", {
        "users": users,
        "role_groups": role_groups,
        "q": q,
    })


@staff_member_required
def admin_toggle_user_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        approved = request.POST.get("approved_publisher")
        club = request.POST.get("club_admin")

        approved_group, _ = Group.objects.get_or_create(name="approved_publisher")
        club_group, _ = Group.objects.get_or_create(name="club_admin")

        # Temizle
        user.groups.remove(approved_group, club_group)

        # Yeniden ata
        if approved:
            user.groups.add(approved_group)
        if club:
            user.groups.add(club_group)

        messages.success(request, f"{user.username} rolleri güncellendi.")

    return redirect("admin_user_roles")


@staff_member_required
@require_POST
# AJAX üzerinden rol atama
def admin_set_user_role(request, user_id):
    """
    Modal’dan gelen role update isteği
    """
    user = get_object_or_404(User, id=user_id)

    # Tek rol seçtireceksen:
    role = request.POST.get("role")  # "approved_publisher" gibi
    allowed = {"approved_publisher", "club_admin", ""}

    if role not in allowed:
        return JsonResponse({"ok": False, "error": "Geçersiz rol"}, status=400)

    # Bu iki grubu yönetiyoruz (istersen genişlet)
    managed_groups = Group.objects.filter(name__in=["approved_publisher", "club_admin"])
    user.groups.remove(*managed_groups)

    if role:
        grp, _ = Group.objects.get_or_create(name=role)
        user.groups.add(grp)

    return JsonResponse({"ok": True})



# ----------------------
# PROFILE
# ----------------------
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    liked_posts = Post.objects.filter(likes__user=request.user)
    return render(request, "profile.html", {"profile": profile, "liked_posts": liked_posts})


# ----------------------
# POST DETAIL + LIKE + COMMENT
# ----------------------
# Post detay, view/like/comment işlemleri
def post_detail(request, pk):
    # Admin/staff: her şeyi görsün. Normal kullanıcı: sadece APPROVED
    if request.user.is_authenticated and request.user.is_staff:
        post = get_object_or_404(Post, pk=pk)
    else:
        post = get_object_or_404(Post, pk=pk, status=Post.Status.APPROVED)

    # görüntülenme kaydı
    if request.user.is_authenticated:
        PostView.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={"last_viewed_at": timezone.now()}
        )

    comments = PostComment.objects.filter(post=post).select_related("user").order_by("-created_at")
    like_count = PostLike.objects.filter(post=post).count()

    liked = False
    if request.user.is_authenticated:
        liked = PostLike.objects.filter(user=request.user, post=post).exists()

    return render(request, "post_detail.html", {
        "post": post,
        "comments": comments,
        "like_count": like_count,
        "liked": liked,
    })


@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)

    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()

    return redirect("post_detail", pk=pk)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    text = (request.POST.get("text") or "").strip()

    if not text:
        messages.error(request, "Yorum boş olamaz.")
        return redirect("post_detail", pk=pk)

    PostComment.objects.create(user=request.user, post=post, text=text)
    messages.success(request, "Yorum eklendi.")
    return redirect("post_detail", pk=pk)

def api_departments(request):
    uni_id = request.GET.get("university_id")
    qs = Department.objects.none()
    if uni_id and uni_id.isdigit():
        qs = Department.objects.filter(university_id=int(uni_id)).order_by("name")

    return JsonResponse({
        "items": [{"id": d.id, "name": d.name} for d in qs]
    })

@require_POST
@login_required
# Kullanıcının AI geçmişini temizler
def clear_ai_history(request):
    AIMessage.objects.filter(user=request.user).delete()
    return redirect("home")    