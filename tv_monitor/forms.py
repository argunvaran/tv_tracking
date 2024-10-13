from django import forms
from .models import TV

class TVForm(forms.ModelForm):
    class Meta:
        model = TV
        fields = ['name', 'ip_address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TV Adı'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IP Adresi'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if TV.objects.filter(name=name).exists():
            raise forms.ValidationError(f"{name} isimli bir TV zaten mevcut.")
        return name

    def clean_ip_address(self):
        ip_address = self.cleaned_data.get('ip_address')
        if TV.objects.filter(ip_address=ip_address).exists():
            raise forms.ValidationError(f"{ip_address} IP adresine sahip bir TV zaten mevcut.")
        return ip_address
