import subprocess
import os
import time

# Define the Celery worker and beat commands
worker_command = "celery -A celery_app worker --loglevel=info -P eventlet"
beat_command = "celery -A celery_app beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info"
server_command = "python manage.py runserver"

# Function to run a command in the background
def run_command_in_background(command):
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    # Start Celery worker and beat in the background
    run_command_in_background(worker_command)
    run_command_in_background(beat_command)

    # Give some time for Celery worker to start
    time.sleep(6)

    # Start Django development server
    subprocess.run(server_command, shell=True)

