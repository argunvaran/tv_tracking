from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class TV(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)  
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def clean(self):
        
        if TV.objects.filter(name=self.name).exclude(id=self.id).exists():
            raise ValidationError(f"{self.name} isimli bir TV zaten mevcut.")

        if TV.objects.filter(ip_address=self.ip_address).exclude(id=self.id).exists():
            raise ValidationError(f"{self.ip_address} IP adresine sahip bir TV zaten mevcut.")

    def save(self, *args, **kwargs):
        
        self.clean()
        super().save(*args, **kwargs)

class TVLog(models.Model):
    tv = models.ForeignKey(TV, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('ON', 'Open'), ('OFF', 'Close')])
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)  

    def __str__(self):
        duration_str = f" for {self.duration}" if self.duration else ""
        return f"{self.tv.name} - {self.status} at {self.timestamp}{duration_str}"
