from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Resource, Quiz, Forum, Enrollment, PaymentScreenshot, UserProfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'date_enrolled')
    search_fields = ('course__title', 'user__username')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'duration', 'students_count', 'price', 'is_free')
    search_fields = ('title', 'instructor')
    list_filter = ('is_free',)

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'url')
    search_fields = ('title', 'course__title')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'url')
    search_fields = ('title', 'course__title')

class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'url', 'user')
    search_fields = ('title', 'course__title', 'user__username')

class PaymentScreenshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'screenshot', 'status')
    search_fields = ('user__username', 'course__title')
    list_filter = ('status',)
    actions = ['approve_screenshot', 'reject_screenshot']

    def approve_screenshot(self, request, queryset):
        for screenshot in queryset:
            if screenshot.status != 'Approved':
                screenshot.status = 'Approved'
                screenshot.save()

                # Enroll the user in the course
                enrollment, created = Enrollment.objects.get_or_create(user=screenshot.user, course=screenshot.course)
                if created:
                    logger.info(f'User {screenshot.user.username} enrolled in {screenshot.course.title}')

                # Send approval email
                try:
                    send_mail(
                        'Payment Approved',
                        f'Hi {screenshot.user.first_name},\n\nYour payment for the course "{screenshot.course.title}" has been approved. You are now enrolled in the course.\n\nBest Regards,\nHimalayan E-Learning Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [screenshot.user.email],
                        fail_silently=False,
                    )
                    logger.info(f'Approval email sent to {screenshot.user.email}')
                except Exception as e:
                    logger.error(f'Error sending approval email: {e}')

        self.message_user(request, "Selected screenshots have been approved and users have been enrolled.")

    def reject_screenshot(self, request, queryset):
        for screenshot in queryset:
            if screenshot.status != 'Rejected':
                screenshot.status = 'Rejected'
                screenshot.save()

                # Send rejection email
                try:
                    send_mail(
                        'Payment Rejected',
                        f'Hi {screenshot.user.first_name},\n\nYour payment for the course "{screenshot.course.title}" has been rejected. Please contact support for more information.\n\nBest Regards,\nHimalayan E-Learning Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [screenshot.user.email],
                        fail_silently=False,
                    )
                    logger.info(f'Rejection email sent to {screenshot.user.email}')
                except Exception as e:
                    logger.error(f'Error sending rejection email: {e}')

        self.message_user(request, "Selected screenshots have been rejected.")

    approve_screenshot.short_description = 'Approve selected payment screenshots'
    reject_screenshot.short_description = 'Reject selected payment screenshots'

# Unregister models if they are already registered
models = [Enrollment, PaymentScreenshot, Course, Resource, Quiz, Forum]
for model in models:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Register the models with their corresponding admin classes
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(PaymentScreenshot, PaymentScreenshotAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Forum, ForumAdmin)
