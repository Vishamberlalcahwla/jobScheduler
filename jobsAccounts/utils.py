from .models import Job
from datetime import datetime
from django.db.models import Q, Case, When, Value, IntegerField
import time
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, DateField
from django.db.models.functions import Now

MAX_PARALLEL_JOBS = 3  # Limit to 3 parallel jobs
today = datetime.today().date()

def process_job(job):
    """Simulate job execution"""
    try:
        job.status = "In Progress"
        job.start_job_time = timezone.now()
        job.save()
        
        # Simulate execution delay
        time.sleep(job.estimated_duration)  # Replace this with actual job processing logic

        job.end_job_time = timezone.now()  # Use timezone-aware datetime
        job.save()

        # Calculate the wait time (ensuring both times are timezone-aware)
        if job.start_job_time and job.end_job_time:
            waiting_time = job.end_job_time - job.start_job_time
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

    # Priority mapping using Case expression
    priority_order = Case(
        When(priority_level="High", then=Value(1)),
        When(priority_level="Medium", then=Value(2)),
        When(priority_level="Low", then=Value(3)),
        default=Value(3),
        output_field=IntegerField()
    )

    # Mark past deadline jobs as failed
    Job.objects.filter(status="Pending", deadline__lt=today).update(status="Failed")
    Job.objects.filter(status="Completed").update(status="Pending")
    # Process jobs until no jobs are pending
    while True:
        # Query to fetch pending jobs, ordered by priority and deadline (Earliest Deadline First)
        pending_jobs = Job.objects.filter(status="Pending").annotate(
            # Calculate the difference between the deadline and today's date
            deadline_diff=ExpressionWrapper(
                F('deadline') - today,
                output_field=IntegerField()
            ),
            priority_order=priority_order  # Annotating priority_order
        ).order_by('priority_order', 'deadline_diff')[:MAX_PARALLEL_JOBS]

        if not pending_jobs.exists():
            print("No more jobs to process. Exiting...")
            break

        # Process jobs in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_JOBS) as executor:
            for job in pending_jobs:
                executor.submit(process_job, job)  # Run job in parallel

        # Check if all jobs are finished (completed or failed)
        all_jobs_finished = not Job.objects.filter(status="Pending").exists()
        if all_jobs_finished:
            print("All jobs finished. Re-fetching pending jobs...")
        else:
            print("Some jobs are still pending. Waiting for them to finish...")
            time.sleep(5)  # Wait before checking again, adjust as needed
