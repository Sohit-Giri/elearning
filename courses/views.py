from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import PaymentScreenshotForm, SignUpForm, CourseForm, UserProfileForm, ContactForm
from .models import ContactQuery, Course, Enrollment, PaymentScreenshot, UserProfile, Resource, Quiz, Forum
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Check if a UserProfile already exists for the user
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(
                    user=user,
                    first_name=form.cleaned_data.get('first_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    profile_photo=form.cleaned_data.get('profile_photo'),
                    mobile_number=form.cleaned_data.get('mobile_number')
                )
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            # Send signup email
            try:
                send_mail(
                    'Welcome to Himalayan E-Learning Platform',
                    f'Hi {user.first_name},\n\nThank you for signing up for our platform.\n\nBest Regards,\nHimalayan E-Learning Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f'Signup email sent to {user.email}')
            except Exception as e:
                logger.error(f'Error sending signup email: {e}')

            messages.success(request, 'Signup successful! You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Signup failed. Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    enrolled_courses = Enrollment.objects.filter(user=request.user).select_related('course')

    context = {
        'form': form,
        'user_profile': user_profile,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user = user_profile.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            user_profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'edit_profile.html', {'form': form})

def home_view(request):
    if request.user.is_authenticated:
        enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    else:
        enrolled_courses = []
    
    paid_courses = Course.objects.filter(is_free=False)
    context = {
        'paid_courses': paid_courses,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'home.html', context)

@login_required
def courses_view(request):
    courses = Course.objects.all()
    enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'courses.html', context)

@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    resources = Resource.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)
    forums = Forum.objects.filter(course=course)
    
    context = {
        'course': course,
        'resources': resources,
        'quizzes': quizzes,
        'forums': forums
    }
    return render(request, 'course_detail.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Check if the user is already enrolled
    if Enrollment.objects.filter(course=course, user=user).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course.id)

    # For free courses, directly enroll the user
    if course.is_free:
        Enrollment.objects.create(course=course, user=user)
        messages.success(request, "You have successfully enrolled in the course.")
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = PaymentScreenshotForm(request.POST, request.FILES)
        if form.is_valid():
            payment_screenshot = form.save(commit=False)
            payment_screenshot.user = user
            payment_screenshot.course = course
            payment_screenshot.save()
            messages.success(request, "Payment screenshot uploaded successfully. You will be enrolled after verification.")
            return redirect('enroll_success')
    else:
        form = PaymentScreenshotForm()

    return render(request, 'enroll.html', {'course': course, 'form': form})

@login_required
def enroll_success(request):
    return render(request, 'enroll_success.html')

@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form, 'course': course})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses')
    return render(request, 'delete_course.html', {'course': course})

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'There was an error sending your message. Please try again.')
    else:
        form = ContactForm()
    
    context = {
        'form': form
    }
    return render(request, 'contact.html', context)
