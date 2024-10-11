from django.urls import path
from .views import contact_view, profile_view, edit_profile_view, course_detail_view, about_view, signup_view, login_view, home_view, logout_view, courses_view, enroll_in_course, add_course, edit_course, delete_course, enroll_success
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('home/', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('courses/', courses_view, name='courses'),
    path('enroll/<int:course_id>/', enroll_in_course, name='enroll_in_course'),
    path('enroll/success/', enroll_success, name='enroll_success'),
    path('contact/', contact_view, name='contact'),
    path('courses/<int:course_id>/', course_detail_view, name='course_detail'),
    path('add_course/', add_course, name='add_course'),
    path('edit_course/<int:course_id>/', edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', delete_course, name='delete_course'),
    path('', login_view),  # Redirect root URL to login view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
