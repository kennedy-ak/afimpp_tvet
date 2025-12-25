"""
URL configuration for afimpp_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('courses/', include('courses.urls')),
    path('users/', include('users.urls')),
    path('contact/', include('contact.urls')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = "AfIMMP Administration"
admin.site.site_title = "AfIMMP Admin Portal"
admin.site.index_title = "Welcome to AfIMMP Administration"