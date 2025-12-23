from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Enrollment, Payment, CourseRegistration
from .forms import EnrollmentForm, PaymentForm, CourseRegistrationForm
import uuid

def course_list(request):
    """List all active courses"""
    courses = Course.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_title__icontains=search_query)
        )
    
    # Filter by level
    level = request.GET.get('level', '')
    if level:
        courses = courses.filter(level=level)
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'selected_level': level,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Display course details"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    is_enrolled = False
    enrollment = None
    
    # Get related courses (same level or same category)
    related_courses = Course.objects.filter(
        is_active=True
    ).exclude(
        pk=course.pk
    ).filter(
        Q(level=course.level) | Q(title__icontains='mining') | Q(title__icontains='quarrying')
    )[:3]
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'related_courses': related_courses,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    """Enroll user in a course"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('course_detail', slug=course.slug)
    
    if request.method == 'POST':
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course,
            status='pending',
            payment_status='pending'
        )
        messages.success(request, f'You have successfully enrolled in {course.title}. Please proceed to payment.')
        return redirect('payment', enrollment_id=enrollment.pk)
    
    context = {
        'course': course,
    }
    return render(request, 'courses/enroll_confirm.html', context)


@login_required
def payment(request, enrollment_id):
    """Handle payment for enrollment"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    if enrollment.payment_status == 'completed':
        messages.info(request, 'Payment for this enrollment has already been completed.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.enrollment = enrollment
            payment.transaction_id = str(uuid.uuid4())
            payment.status = 'completed'  # In production, this would be pending until verified
            payment.save()
            
            # Update enrollment payment status
            if payment.amount >= enrollment.course.price:
                enrollment.payment_status = 'completed'
                enrollment.status = 'approved'
            else:
                enrollment.payment_status = 'partial'
            
            enrollment.save()
            
            messages.success(request, 'Payment successful! You are now enrolled in the course.')
            return redirect('dashboard')
    else:
        form = PaymentForm(initial={'amount': enrollment.course.price})
    
    context = {
        'enrollment': enrollment,
        'form': form,
    }
    return render(request, 'courses/payment.html', context)


@login_required
def course_registration(request, enrollment_id):
    """Handle comprehensive course registration form"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    # Check if registration already exists
    if hasattr(enrollment, 'registration'):
        messages.info(request, 'You have already completed the registration form for this course.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.enrollment = enrollment
            registration.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    f'New Course Registration: {registration.full_name}',
                    f'A new student has registered for {enrollment.course.title}.\n\n'
                    f'Student Details:\n'
                    f'Name: {registration.full_name}\n'
                    f'Email: {registration.email_address}\n'
                    f'Phone: {registration.phone_number}\n'
                    f'Course: {enrollment.course.title}\n'
                    f'Registration Date: {registration.created_at}\n\n'
                    f'Please log in to the admin panel to review the application.',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(request, 'Registration form submitted successfully! You will be notified once your application is reviewed.')
            return redirect('dashboard')
    else:
        # Pre-populate form with user data if available
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email_address': request.user.email,
            'phone_number': request.user.phone,
        }
        form = CourseRegistrationForm(initial=initial_data)
    
    context = {
        'enrollment': enrollment,
        'form': form,
    }
    return render(request, 'courses/course_registration.html', context)


@login_required
def dashboard(request):
    """User dashboard showing enrollments"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # Create a list with enrollment data including registration status
    enrollment_data = []
    for enrollment in enrollments:
        enrollment_data.append({
            'enrollment': enrollment,
            'needs_registration': not hasattr(enrollment, 'registration')
        })
    
    context = {
        'enrollment_data': enrollment_data,
    }
    return render(request, 'courses/dashboard.html', context)