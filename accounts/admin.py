# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Personnalisation de l'admin pour les utilisateurs
admin.site.unregister(User)
admin.site.register(User, UserAdmin)