# newsletter/models.py
from django.db import models
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class NewsletterCampaign(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='newsletters/', blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    def send(self):
        if not self.is_sent:
            subscribers = Subscriber.objects.filter(is_active=True)
            emails = []
            for sub in subscribers:
                html = render_to_string('newsletter/email_template.html', {
                    'subscriber': sub,
                    'campaign': self
                })
                emails.append((self.subject, html, 'noreply@lozashop.com', [sub.email]))
            
            send_mass_mail(emails, fail_silently=False)
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save()
    
    def __str__(self):
        return self.subject