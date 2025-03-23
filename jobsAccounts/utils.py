from .models import Job
from datetime import datetime
from django.db.models import Q, Case, When, Value, IntegerField
import time
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from datetime import timedelta
MAX_PARALLEL_JOBS = 3  # Limit to 3 parallel jobs

def process_job(job):
    """Simulate job execution"""
    try:
        job.status          = "In Progress"
        job.start_job_time  = timezone.now()
        job.save()
        
        # Simulate execution delay
        time.sleep(job.estimated_duration)  # Replace this with actual job processing logic

        job.end_job_time = timezone.now()  # Use timezone-aware datetime
        job.save()

        # Calculate the wait time (ensuring both times are timezone-aware)
        if job.start_job_time and job.end_job_time:
            waiting_time  = job.end_job_time - job.start_job_time
            # job.wait_time = waiting_time
            job.average_wait_time = waiting_time.total_seconds() / 60  # Convert to minutes
            job.save()

        # Mark job as completed
        job.status = "Completed"
        job.save()
        print(f"✅ Job Completed: {job.job_name}")

    except Exception as e:
        job.status = "Failed"
        job.save()
        print(f"❌ Job Failed: {job.job_name} - {str(e)}")


def schedule_jobs():
    """Schedule jobs based on priority and deadline"""

    today = datetime.today().date()

    # Annotate priority levels for sorting
    priority_order = Case(
        When(priority_level="High", then=Value(1)),
        When(priority_level="Medium", then=Value(2)),
        When(priority_level="Low", then=Value(3)),
        output_field=IntegerField(),
    )

    # Mark past deadline jobs as failed
    Job.objects.filter(status="Pending", deadline__lt=today).update(status="Failed")

    # Fetch jobs with today's deadline first, then future ones
    pending_jobs = Job.objects.filter(
        status="Pending"
    ).annotate(
        priority_order=priority_order,
        is_today=Case(
            When(deadline=today, then=Value(1)),  # Jobs with today's deadline first
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).order_by('-is_today', 'priority_order', 'deadline')[:MAX_PARALLEL_JOBS]

    if not pending_jobs.exists():
        print("No jobs to process.")
        return

    # Process jobs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_JOBS) as executor:
        for job in pending_jobs:
            executor.submit(process_job, job)  # Run job in parallel
