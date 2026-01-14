# Django'nun form sistemini içe aktarır
from django import forms

# Aynı uygulama içindeki Profile modelini içe aktarır
from .models import Profile


# Profile modeli için oluşturulmuş ModelForm sınıfı
# ModelForm, model alanlarını otomatik olarak form alanlarına dönüştürür
class ProfileForm(forms.ModelForm):

    # Formun yapılandırmasını yapan iç sınıf
    class Meta:
        # Bu formun bağlı olduğu Django modeli
        model = Profile

        # Formda kullanıcıya gösterilecek model alanları
        fields = [
            "university",              # Kullanıcının üniversitesi
            "department",              # Kullanıcının bölümü
            "avatar",                  # Profil fotoğrafı
            "notifications_enabled",   # Bildirim ayarı (aktif/pasif)
        ]

        # Form alanlarının kullanıcıya gösterilecek etiketleri (label)
        labels = {
            "university": "Üniversite",            # Üniversite alanı etiketi
            "department": "Bölüm",                 # Bölüm alanı etiketi
            "avatar": "Profil Fotoğrafı",          # Profil resmi etiketi
            "notifications_enabled": "Bildirimler" # Bildirim ayarı etiketi
        }

        # Form alanlarında kullanılacak HTML widget'ları
        # Widget'lar, alanların nasıl render edileceğini belirler
        widgets = {
            # Üniversite alanı için <select> HTML elementi
            "university": forms.Select(attrs={
                "class": "un-input form-control-custom"  # CSS sınıfları
            }),

            # Bölüm alanı için <input type="text">
            "department": forms.TextInput(attrs={
                "class": "un-input form-control-custom", # CSS sınıfları
                "placeholder": "Örn: Bilgisayar Mühendisliği"  # Kullanıcıya ipucu
            }),

            # Avatar alanı için dosya yükleme input'u
            "avatar": forms.ClearableFileInput(attrs={
                "class": "un-input form-control-custom"  # CSS sınıfları
            }),

            # Bildirim ayarı için checkbox input'u
            "notifications_enabled": forms.CheckboxInput(attrs={
                "class": "un-checkbox form-check-input-custom"  # Özel checkbox stili
            }),
        }
