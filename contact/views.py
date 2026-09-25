from django.shortcuts import render, redirect
from django.contrib import messages
from afimpp_config.analytics import capture
from .forms import ContactForm

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            capture(request, 'contact_form_submitted')
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
            }
        form = ContactForm(initial=initial_data)
    
    context = {
        'form': form,
    }
    return render(request, 'contact/contact.html', context)