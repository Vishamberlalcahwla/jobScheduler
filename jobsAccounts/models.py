from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    job_name = models.CharField(max_length=255)
    estimated_duration = models.IntegerField()  # In seconds
    priority_level = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    deadline = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)    
    # New fields
    start_job_time = models.DateTimeField(null=True, blank=True)  # When the job starts
    end_job_time = models.DateTimeField(null=True, blank=True)    # When the job ends
    wait_time = models.IntegerField(default=0)  # Average wait time in seconds
    average_wait_time = models.FloatField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['priority_level', 'deadline']),  # Index for job scheduling
        ]

    def __str__(self):
        return self.job_name

    @property
    def get_wait_time(self):
        """Returns the wait time (difference between created_at and start_job_time)."""
        if self.start_job_time:
            return (self.start_job_time - self.created_at).seconds
        return 0
