from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    courses_enrolled = models.ManyToManyField('Course', related_name='enrolled_users')

    def __str__(self):
        return self.user.username

class Course(models.Model):
    title = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.DurationField()
    students_count = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    students_enrolled = models.ManyToManyField('auth.User', related_name='enrolled_courses')

    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'
    
class PaymentScreenshot(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    
class Resource(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')

class Forum(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ContactQuery(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
