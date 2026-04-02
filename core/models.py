from django.db import models

class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/', max_length=500)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', '-uploaded_at']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-subscribed_at']


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="AfIMMP Technical and Vocational Training Center")
    site_email = models.EmailField(default="info@afimpp.edu.gh")
    site_phone = models.CharField(max_length=50, blank=True, null=True)
    site_address = models.CharField(max_length=300, default="Tarkwa-Ghana")

    # About Section
    about_title = models.CharField(max_length=200, default="Know more about AfIMMP-TVET")
    about_description = models.TextField()
    about_paragraph_2 = models.TextField(blank=True, null=True)
    about_image = models.ImageField(upload_to='about/', blank=True, null=True, max_length=500)

    # Mission, Vision, Core Values
    mission_statement = models.TextField(default="Our Mission is to promote excellence in the mining industry through professional development, knowledge sharing, and ethical practices, while contributing to sustainable development and socioeconomic growth in Ghana,")
    vision_statement = models.TextField(default="Our Mission is to promote excellence in the mining industry through professional development, knowledge sharing, and ethical practices, while contributing to sustainable development and socioeconomic growth in Ghana,")
    core_values = models.TextField(default="We have a culture that is modern, relevant, and inspires students to have a brighter future. We are determined in our approach to learning, are creative in our thinking, and bold in our ambitions.")

    # Statistics
    courses_count = models.IntegerField(default=1)
    lecturers_count = models.IntegerField(default=3)
    students_count = models.IntegerField(default=10)

    # Hero Section
    hero_title = models.CharField(max_length=200, default="Best Education For better Future")
    hero_subtitle = models.CharField(max_length=300, default="Unlock your bright career AfIMMP TVeT")
    hero_description = models.TextField(default="This is where we teach students skills they need to transform themselves, others, and our global communities.")

    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'