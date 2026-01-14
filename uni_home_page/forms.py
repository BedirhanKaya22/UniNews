# Django'nun form sistemini kullanabilmek için import edilir
from django import forms

# Post modelini post gönderme formunda kullanmak için import eder
from .models import Post

# Kullanıcı profilini güncellemek için Profile modelini import eder
from profile_view.models import Profile

# Üniversite ve bölüm modelleri (şu an direct kullanılmasa da proje bağlamında mevcut)
from profile_view.models import University, Department

# Django'nun varsayılan User modeli
from django.contrib.auth.models import User


# =========================
# PROFİL GÜNCELLEME FORMU
# =========================
class ProfileUpdateForm(forms.ModelForm):
    """
    Kullanıcının profil bilgilerini (avatar, üniversite, bölüm vb.)
    güncelleyebilmesi için kullanılan ModelForm
    """
    class Meta:
        # Bu formun hangi modele bağlı olduğunu belirtir
        model = Profile

        # Profil modelinden formda gösterilecek alanlar
        fields = ["avatar", "university", "department", "notifications_enabled"]


# =========================
# HABER / POST GÖNDERME FORMU
# =========================
class PostSubmitForm(forms.ModelForm):
    """
    Kullanıcıların yeni haber (Post) göndermesi için kullanılan form
    """
    class Meta:
        # Formun bağlı olduğu model
        model = Post

        # Post modelinden formda yer alacak alanlar
        fields = ["title", "category", "summary", "content", "cover"]

        # Form alanlarının kullanıcıya görünen etiketleri
        labels = {
            "title": "Haber Başlığı",
            "category": "Kategori",
            "summary": "Kısa Açıklama",
            "content": "Haber İçeriği",
            "cover": "Kapak Görseli",
        }

        # Alanlara özel HTML widget ve CSS class ayarları
        widgets = {
            # Başlık input alanı
            "title": forms.TextInput(attrs={
                "class": "un-input",
                "placeholder": "Örn: Final haftası kütüphane 24 saat açık"
            }),

            # Kategori dropdown/select alanı
            "category": forms.Select(attrs={"class": "un-input"}),

            # Özet alanı (kısa açıklama)
            "summary": forms.TextInput(attrs={
                "class": "un-input",
                "placeholder": "1-2 cümle kısa açıklama (opsiyonel)"
            }),

            # İçerik alanı (textarea)
            "content": forms.Textarea(attrs={
                "class": "un-input un-textarea",
                "rows": 6,
                "placeholder": "Haber detaylarını buraya yaz..."
            }),

            # Kapak görseli dosya upload alanı
            "cover": forms.ClearableFileInput(attrs={"class": "un-input"}),
        }

    # =========================
    # BAŞLIK DOĞRULAMA
    # =========================
    def clean_title(self):
        """
        Başlığın minimum uzunlukta olmasını kontrol eder
        """
        # Başlığı alır, None gelirse boş string yapar ve baş/son boşlukları siler
        title = (self.cleaned_data.get("title") or "").strip()

        # Başlık en az 5 karakter değilse hata fırlatır
        if len(title) < 5:
            raise forms.ValidationError("Başlık en az 5 karakter olmalı.")

        # Doğrulanmış başlığı geri döner
        return title


# =========================
# KAYIT FORMU
# =========================
class RegisterForm(forms.Form):
    """
    Kullanıcı kayıt işlemi için kullanılan klasik Form (ModelForm değil)
    """

    # Kullanıcı adı alanı
    username = forms.CharField(max_length=150)

    # E-posta alanı
    email = forms.EmailField()

    # Üniversite adı (artık select değil, manuel yazma)
    university_name = forms.CharField(max_length=255)

    # Bölüm adı (manuel yazma)
    department_name = forms.CharField(max_length=255)

    # Şifre alanı (gizli input)
    password1 = forms.CharField(widget=forms.PasswordInput)

    # Şifre tekrar alanı
    password2 = forms.CharField(widget=forms.PasswordInput)

    # =========================
    # ÜNİVERSİTE ADI TEMİZLEME
    # =========================
    def clean_university_name(self):
        """
        Üniversite adındaki baş/son boşlukları temizler
        """
        return (self.cleaned_data.get("university_name") or "").strip()

    # =========================
    # BÖLÜM ADI TEMİZLEME
    # =========================
    def clean_department_name(self):
        """
        Bölüm adındaki baş/son boşlukları temizler
        """
        return (self.cleaned_data.get("department_name") or "").strip()

    # =========================
    # FORM GENEL DOĞRULAMA
    # =========================
    def clean(self):
        """
        Şifrelerin birbiriyle eşleşip eşleşmediğini kontrol eder
        """
        cleaned = super().clean()

        # Girilen şifreleri alır
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        # İkisi de varsa ve eşleşmiyorsa hata fırlatır
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")

        return cleaned


# =========================
# UNINEWS AI SORU FORMU
# =========================
class uninewsaiform(forms.Form):
    """
    UniNews AI'ye soru sormak için kullanılan basit form
    """

    # Kullanıcının sorusunu aldığı text input
    question = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            "placeholder": "UniNews AI’ye soru sor...",
        })
    )
