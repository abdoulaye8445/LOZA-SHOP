# newsletter/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subscriber

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name', '')
        
        if email:
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                subscriber.name = name
                subscriber.save()
                messages.success(request, '✅ Merci pour votre inscription à la newsletter !')
            else:
                messages.info(request, 'ℹ️ Vous êtes déjà inscrit à la newsletter.')
        else:
            messages.error(request, '❌ Veuillez entrer une adresse email valide.')
    return redirect('products:home')

def unsubscribe(request, email):
    subscriber = get_object_or_404(Subscriber, email=email)
    subscriber.is_active = False
    subscriber.save()
    messages.success(request, '✅ Vous êtes désinscrit de la newsletter.')
    return redirect('products:home')