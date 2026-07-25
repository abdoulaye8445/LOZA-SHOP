# notifications/models.py
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = [
        ('order', 'Commande'),
        ('promotion', 'Promotion'),
        ('newsletter', 'Newsletter'),
        ('system', 'Système'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"