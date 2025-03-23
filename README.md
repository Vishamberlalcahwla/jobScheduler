# Job Scheduler

This is a Job Scheduler application built with Django and Python, designed to simulate the scheduling and execution of jobs based on priority and deadline. The system processes jobs concurrently using Python's `ThreadPoolExecutor`.

## Features:
- **Job Priority**: Jobs are scheduled based on priority levels (High, Medium, Low).
- **Earliest Deadline First (EDF)**: Jobs are ordered by their deadlines, with jobs having earlier deadlines processed first.
- **Concurrency**: Jobs are processed concurrently up to a maximum limit (configurable).
- **Job Execution Simulation**: Each job has an estimated duration, and its execution is simulated using `time.sleep`.
- **Job Status**: Jobs can have statuses such as "Pending", "In Progress", "Completed", or "Failed".

## Prerequisites

Before running the project, ensure you have the following installed:

1. **Python 3.8+**: The application is built with Python.
2. **Django**: The framework used to build this application.
3. **Database**: A database like PostgreSQL or SQLite is required for storing job data.
4. **pip**: Python's package installer.

## Installation

Follow these steps to get the project running locally:

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/Vishamberlalcahwla/jobScheduler.git
cd jobScheduler
