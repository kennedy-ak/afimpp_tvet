from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from afimpp_config.analytics import capture
from courses.models import Course
from .models import GalleryImage, SiteSettings, Newsletter
from .forms import NewsletterForm
from contact.forms import ContactForm

def home(request):
    """Homepage view"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    featured_courses = Course.objects.filter(is_active=True, featured=True)[:3]
    gallery_images = GalleryImage.objects.filter(is_active=True)[:6]
    
    # Newsletter form
    if request.method == 'POST' and 'newsletter_submit' in request.POST:
        newsletter_form = NewsletterForm(request.POST)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data['email']
            if not Newsletter.objects.filter(email=email).exists():
                newsletter_form.save()
                capture(request, 'newsletter_subscribed')
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
            return redirect('home')
    else:
        newsletter_form = NewsletterForm()
    
    context = {
        'site_settings': site_settings,
        'featured_courses': featured_courses,
        'gallery_images': gallery_images,
        'newsletter_form': newsletter_form,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page view"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None

    # Get gallery images for the gallery section
    gallery_images = GalleryImage.objects.filter(is_active=True)[:6]

    context = {
        'site_settings': site_settings,
        'gallery_images': gallery_images,
    }
    return render(request, 'core/about.html', context)


def gallery(request):
    """Gallery page view"""
    gallery_images = GalleryImage.objects.filter(is_active=True)
    
    context = {
        'gallery_images': gallery_images,
    }
    return render(request, 'core/gallery.html', context)


def terms_conditions(request):
    """Terms and Conditions page view"""
    return render(request, 'core/terms_conditions.html')